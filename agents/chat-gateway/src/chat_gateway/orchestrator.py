from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
from project_core.config.loader import load_project_config
from project_core.domain.access.acl import build_permissions_snapshot
from project_core.domain.access.user_claims import claims_from_user_dict
from project_core.domain.access.context_policy import ContextPolicy
from project_core.domain.budget import SessionTraceBudget, TraceBudget
from project_core.domain.clarification.bridge import ClarificationBridge
from project_core.domain.clarification.resolver import apply_clarification_reply
from project_core.domain.brief.session_merge import empty_follow_up_message, session_merge_brief
from project_core.domain.contracts.brief import AnalysisBrief, DomainFactTeachPayload
from project_core.domain.contracts.clarification import ClarificationReply, ClarificationRequest
from project_core.domain.contracts.feedback import (
    DomainEvidence,
    DomainRuleCandidate,
    SatisfactionSignal,
)
from project_core.domain.contracts.pipeline import ChatResponse
from project_core.domain.contracts.workflow import AnalysisOutcome, WorkflowStatus
from project_core.domain.errors.codes import (
    BudgetExceededError,
    ClarifyRoundsExceededError,
    PermissionsUnavailableError,
)
from project_core.domain.feedback.analysis_tool_registry import AnalysisToolRegistry
from project_core.domain.feedback.domain_rule_store import DomainRuleStore
from project_core.domain.feedback.loop import CaseStudyIndexer, FeedbackLoop
from project_core.domain.feedback.schema_link_normalize import normalize_schema_links
from project_core.domain.feedback.store import BehavioralSignal
from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog
from project_core.domain.memory.context_pack import (
    append_compact_archive,
    apply_curator_selection,
    assemble_context_pack,
    build_context_pack_hard,
    merge_ccs_patch,
    refresh_working_memory_from_brief,
)
from project_core.domain.memory.session_bundle import SessionBundle, TranscriptTurn
from project_core.domain.memory.working_memory import CompactArchiveEntry, WorkingMemory
from project_core.domain.retrieval.mongo_vector import HybridMongoRetriever
from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.workflow.state import new_workflow, resume_analysis, start_analysis
from project_core.domain.time import utc_now
from project_core.infra.stm.redis_store import RedisSessionStore
from project_core.infra.analysis_repository import sanitize_public_data
from project_core.infra.resilience import CircuitBreaker
from project_core.orchestration.cancellation import CancellationToken, mark_cancelled
from project_core.orchestration.clarification_coordinator import ClarificationCoordinator
from project_core.orchestration.pipeline import SupermarketAnalysisPipeline

from chat_gateway.clients import HttpAgentInvoker, HttpSqlGatewayClient

logger = logging.getLogger(__name__)

_NEGATIVE_OUTCOMES = frozenset({"error", "impossible", "policy_blocked", "partial"})


class ChatOrchestrator:
    def __init__(self) -> None:
        self.stm = RedisSessionStore()
        self.cfg = load_project_config()
        self.context_policy = ContextPolicy()
        self.clarify = ClarificationCoordinator(
            bridge=ClarificationBridge(min_confidence=self.cfg.clarification.bridge_min_confidence),
        )
        # mimo / large prompts often exceed 120s per agent call; keep in sync with
        # pipeline.max_sync_seconds and OpenRouterClient timeout.
        self._http = httpx.Client(timeout=600.0)
        self._agent_circuit = CircuitBreaker()
        self._sql_circuit = CircuitBreaker()
        self._cancel_tokens: dict[str, CancellationToken] = {}
        self.feedback: FeedbackLoop | None = None
        self.analysis_tool_registry: AnalysisToolRegistry | None = None
        self.domain_rule_store: DomainRuleStore | None = None
        # Optional sinks used by the durable worker to mirror pipeline progress
        # into Mongo analysis_events + live-trial JSONL without changing agent logic.
        self.progress_sinks: list[Any] = []
        try:
            from pymongo import MongoClient

            from project_core.domain.analysis.recipe_runtime import set_registry
            from project_core.llm.embedding_client import EmbeddingClient

            mongo_timeout = int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", "2000"))
            mongo = MongoClient(
                os.getenv("MONGODB_URI", "mongodb://localhost:18217/supermarket_agent"),
                serverSelectionTimeoutMS=mongo_timeout,
            )
            mongo.admin.command("ping")
            db = mongo.get_default_database()
            indexer = CaseStudyIndexer(db["case_studies"])

            def _embed_text(text: str) -> list[float]:
                return EmbeddingClient().embed([text])[0]

            retriever = HybridMongoRetriever(db)
            self.analysis_tool_registry = AnalysisToolRegistry(db["analysis_tools"], embed_fn=_embed_text)
            set_registry(self.analysis_tool_registry)
            self.domain_rule_store = DomainRuleStore(db["domain_rules"])
            self.feedback = FeedbackLoop(
                indexer=indexer,
                retriever=retriever,
                embed_fn=_embed_text,
                tool_registry=self.analysis_tool_registry,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Mongo/RAG unavailable: %s", exc)
        self.pipeline = SupermarketAnalysisPipeline(
            agent_invoker=HttpAgentInvoker(client=self._http, circuit=self._agent_circuit),
            sql_gateway=HttpSqlGatewayClient(client=self._http, circuit=self._sql_circuit),
            catalog=SchemaCatalog.from_dictionary_dir(),
            feedback_loop=self.feedback,
            analysis_tool_registry=self.analysis_tool_registry,
            domain_rule_store=self.domain_rule_store,
        )

    def close(self) -> None:
        self._http.close()
        if hasattr(self.pipeline.agent_invoker, "close"):
            self.pipeline.agent_invoker.close()  # type: ignore[attr-defined]
        if hasattr(self.pipeline.sql_gateway, "close"):
            self.pipeline.sql_gateway.close()  # type: ignore[attr-defined]

    def request_cancel(self, session_id: str) -> bool:
        """Signal an in-flight legacy pipeline without making memory authoritative."""
        token = self._cancel_tokens.get(session_id)
        if token is None:
            return False
        token.cancel()
        return True

    def _make_invoker(self) -> HttpAgentInvoker:
        return HttpAgentInvoker(client=self._http, circuit=self._agent_circuit)

    def handle_chat(self, *, session_id: str, message: str, user: dict[str, Any]) -> ChatResponse:
        actor_id, role, store_ids = claims_from_user_dict(user)
        bundle = self.stm.load_session(session_id)
        if bundle.workflow is None:
            bundle.workflow = new_workflow(session_id, actor_id)

        self._refresh_workflow_staleness(session_id, bundle)

        if self.clarify.on_ingress_clarify(bundle):
            return self._resume_from_pending_clarification(
                session_id=session_id,
                message=message,
                user=user,
                bundle=bundle,
            )

        self._maybe_emit_re_ask_signal(session_id, bundle, message)

        # Per user-turn analysis budget (curator + ingress run before start_analysis).
        bundle.workflow.budget_spent = {}

        turn = TranscriptTurn(id=str(uuid4()), role="user", content=message, at=utc_now().isoformat())
        bundle.transcript.append(turn)
        # Soft L0 bound may mutate compact_archive on workflow
        if bundle.workflow.working_memory is None:
            bundle.workflow.working_memory = WorkingMemory()
        self.stm.save_transcript(session_id, bundle.transcript)

        invoker = self._make_invoker()
        self._cancel_tokens[session_id] = CancellationToken()
        session_budget = self._session_budget(bundle)
        external_sources = []
        if bundle.workflow.brief and bundle.workflow.brief.external_sources:
            external_sources = [s.model_dump() for s in bundle.workflow.brief.external_sources]

        try:
            pack = self._prepare_context_pack(
                bundle=bundle,
                message=message,
                current_turn_id=turn.id,
                external_sources=external_sources,
                invoker=invoker,
                session_budget=session_budget,
                actor_id=actor_id,
                session_id=session_id,
            )
            self.stm.save_workflow(session_id, bundle.workflow)
            ingress = self._invoke_agent_i(
                invoker,
                {"text": message, "external_sources": external_sources},
                {
                    "mode": "ingress",
                    "session_id": session_id,
                    "actor_id": actor_id,
                    "context_pack": pack.to_ingress_user_content(),
                },
                session_budget,
                bundle,
            )
        except BudgetExceededError as exc:
            return ChatResponse(
                session_id=session_id,
                workflow_status=bundle.workflow.status.value,
                message=str(exc),
                error={"code": "BUDGET_EXCEEDED", "retryable": False},
            )

        self._handle_satisfaction_signal(ingress, bundle)

        route = ingress.get("route", "analysis")
        dialogue_act = ingress.get("dialogue_act")
        if dialogue_act == "teach_domain_fact" or ingress.get("domain_fact"):
            return self._handle_teach_domain_fact(
                session_id=session_id,
                message=message,
                user=user,
                bundle=bundle,
                ingress=ingress,
            )
        if route == "confirm_cancel":
            return self._handle_confirm_cancel(session_id, bundle, ingress)
        if route == "wait":
            assistant = TranscriptTurn(
                id=str(uuid4()),
                role="assistant",
                content=ingress.get("user_message", "Đã ghi nhận."),
                at=utc_now().isoformat(),
            )
            bundle.transcript.append(assistant)
            self.stm.save_transcript(session_id, bundle.transcript)
            return ChatResponse(
                session_id=session_id,
                workflow_status=bundle.workflow.status.value,
                message=ingress.get("user_message", "Đã ghi nhận."),
            )

        retry = self._maybe_rephrase_retry(
            session_id=session_id,
            ingress=ingress,
            bundle=bundle,
            permissions=self._build_permissions(actor_id, role, store_ids),
            invoker=invoker,
            session_budget=session_budget,
        )
        if retry is not None:
            return retry

        if route != "analysis":
            assistant = TranscriptTurn(
                id=str(uuid4()),
                role="assistant",
                content=ingress.get("user_message", ""),
                at=utc_now().isoformat(),
            )
            bundle.transcript.append(assistant)
            self.stm.save_transcript(session_id, bundle.transcript)
            return ChatResponse(
                session_id=session_id,
                workflow_status=WorkflowStatus.IDLE.value,
                message=ingress.get("user_message", ""),
            )

        brief = AnalysisBrief.model_validate(ingress.get("brief") or {"intent": message})
        if bundle.workflow.brief and bundle.workflow.brief.external_sources:
            brief.external_sources = bundle.workflow.brief.external_sources

        brief, route_override = session_merge_brief(
            brief=brief,
            dialogue_act=dialogue_act,
            prior_brief=bundle.workflow.last_resolved_brief,
            working_memory=bundle.workflow.working_memory,
            current_message=message,
        )
        if route_override == "chitchat" or brief is None:
            ask = empty_follow_up_message()
            assistant = TranscriptTurn(
                id=str(uuid4()),
                role="assistant",
                content=ask,
                at=utc_now().isoformat(),
            )
            bundle.transcript.append(assistant)
            self.stm.save_transcript(session_id, bundle.transcript)
            return ChatResponse(
                session_id=session_id,
                workflow_status=WorkflowStatus.IDLE.value,
                message=ask,
            )

        analysis_id = start_analysis(bundle.workflow, reset_clarify=True)
        bundle.workflow.brief = brief
        permissions = self._build_permissions(actor_id, role, store_ids)
        bundle.workflow.permissions_snapshot = permissions
        self.stm.save_workflow(session_id, bundle.workflow)

        return self._run_pipeline_and_respond(
            session_id=session_id,
            analysis_id=analysis_id,
            brief=brief,
            bundle=bundle,
            permissions=permissions,
            invoker=invoker,
            session_budget=session_budget,
        )

    def handle_clarify(
        self,
        *,
        session_id: str,
        reply: ClarificationReply,
        user: dict[str, Any],
    ) -> ChatResponse:
        bundle = self.stm.load_session(session_id)
        if bundle.workflow is None or not bundle.clarification:
            return ChatResponse(
                session_id=session_id,
                workflow_status=WorkflowStatus.IDLE.value,
                message="No pending clarification",
                error={"code": "NO_PENDING_CLARIFICATION", "retryable": False},
            )
        request = ClarificationRequest.model_validate(bundle.clarification)
        brief = bundle.workflow.brief or request.partial_brief
        self._stage_reusable_clarification_facts(
            request=request,
            reply=reply,
            user=user,
            trace_id=reply.analysis_id,
        )
        brief = apply_clarification_reply(brief, reply, request)
        bundle.workflow.brief = brief
        resume_analysis(bundle.workflow)
        self.stm.save_clarification(session_id, None)
        self.stm.save_workflow(session_id, bundle.workflow)

        permissions = bundle.workflow.permissions_snapshot or self._build_permissions(*claims_from_user_dict(user))
        invoker = self._make_invoker()
        session_budget = self._session_budget(bundle)
        self._cancel_tokens[session_id] = CancellationToken()
        return self._run_pipeline_and_respond(
            session_id=session_id,
            analysis_id=reply.analysis_id,
            brief=brief,
            bundle=bundle,
            permissions=permissions,
            invoker=invoker,
            session_budget=session_budget,
        )

    def stage_domain_rule(
        self,
        candidate: DomainRuleCandidate,
        *,
        trace_id: str,
        user: dict[str, Any],
    ) -> dict[str, str]:
        if self.domain_rule_store is None:
            return {"status": "no_store"}
        actor_id = str(user["sub"])
        role = self._domain_rule_role(user)
        tenant_id = str(user.get("tenant_id") or "")
        scope = candidate.scope
        if role == "requester":
            scope = "user"
        elif role == "domain_owner" and scope == "global":
            scope = "tenant"
        evidence = [
            item.model_copy(
                update={
                    "source_kind": "user_statement",
                    "actor_id": actor_id,
                    "trace_id": item.trace_id or trace_id,
                    "confidence": 1.0,
                    "independent_group": f"user:{actor_id}",
                }
            )
            for item in candidate.evidence
        ]
        if not evidence and candidate.statement.strip():
            evidence = [
                DomainEvidence(
                    source_kind="user_statement",
                    source_ref="domain_rules_api",
                    quote=candidate.statement,
                    actor_id=actor_id,
                    trace_id=trace_id,
                    schema_links=list(candidate.schema_links),
                    confidence=1.0,
                    independent_group=f"user:{actor_id}",
                )
            ]
        staged = candidate.model_copy(
            update={
                "scope": scope,
                "actor_id": actor_id,
                "tenant_id": tenant_id,
                "authority": role,
                "evidence": evidence,
            }
        )
        rule_id = self.domain_rule_store.stage_candidate(staged, trace_id=trace_id)
        return {"status": "ok", "rule_id": rule_id}

    def list_domain_rules(
        self,
        *,
        user: dict[str, Any],
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        if self.domain_rule_store is None:
            return []
        records = self.domain_rule_store.list_rules(
            actor_id=str(user["sub"]),
            tenant_id=str(user.get("tenant_id") or ""),
            role=self._domain_rule_role(user),
            status=status,
            limit=limit,
            offset=offset,
        )
        return [sanitize_public_data(item) for item in records]

    def review_domain_rule(
        self,
        rule_id: str,
        *,
        action: str,
        user: dict[str, Any],
    ) -> dict[str, str]:
        if self.domain_rule_store is None:
            return {"status": "no_store"}
        self.domain_rule_store.review(
            rule_id,
            action=action,
            actor_id=str(user["sub"]),
            role=self._domain_rule_role(user),
            tenant_id=str(user.get("tenant_id") or ""),
        )
        return {"status": "ok"}

    def confirm_domain_rule(self, rule_id: str, *, confirmed: bool, user: dict[str, Any]) -> dict[str, str]:
        return self.review_domain_rule(
            rule_id,
            action="confirm" if confirmed else "reject",
            user=user,
        )

    def attach_external_sources(self, session_id: str, sources: list[dict[str, Any]]) -> None:
        bundle = self.stm.load_session(session_id)
        if bundle.workflow is None:
            bundle.workflow = new_workflow(session_id, "unknown")
        brief = bundle.workflow.brief or AnalysisBrief()
        from project_core.domain.contracts.external_source import ExternalSource

        existing = {s.file_id for s in brief.external_sources}
        for raw in sources:
            src = ExternalSource.model_validate(raw)
            if src.file_id not in existing:
                brief.external_sources.append(src)
        bundle.workflow.brief = brief
        self.stm.save_workflow(session_id, bundle.workflow)

    def analysis_status(self, analysis_id: str, *, actor_id: str | None = None) -> dict[str, Any]:
        found = self.stm.find_by_analysis_id(analysis_id)
        if not found:
            return {"analysis_id": analysis_id, "status": "not_found"}
        session_id, workflow = found
        if actor_id is not None and str(workflow.actor_id) != str(actor_id):
            return {"analysis_id": analysis_id, "status": "forbidden"}
        return {
            "analysis_id": analysis_id,
            "session_id": session_id,
            "status": workflow.status.value,
            "last_outcome": workflow.last_outcome,
            "progress_step": workflow.progress_step,
            "active_analysis_id": workflow.active_analysis_id,
            "clarify_round": str(workflow.clarify_round),
        }

    def record_artifact_download(self, session_id: str, trace_id: str) -> None:
        if not self.feedback:
            return
        self.feedback.on_behavioral_signal(
            session_id,
            BehavioralSignal(
                session_id=session_id,
                signal_type="download",
                trace_id=trace_id,
                weight=0.3,
            ),
        )

    def _stage_reusable_clarification_facts(
        self,
        *,
        request: ClarificationRequest,
        reply: ClarificationReply,
        user: dict[str, Any],
        trace_id: str,
    ) -> None:
        if self.domain_rule_store is None:
            return
        actor_id = str(user["sub"])
        tenant_id = str(user.get("tenant_id") or "")
        authority = self._domain_rule_role(user)
        for candidate in self.clarify.reusable_candidates_from_reply(
            request=request,
            reply=reply,
            actor_id=actor_id,
            tenant_id=tenant_id,
            authority=authority,
            trace_id=trace_id,
        ):
            self.domain_rule_store.stage_candidate(candidate, trace_id=trace_id)

    @staticmethod
    def _domain_rule_role(user: dict[str, Any]) -> str:
        role = str(user.get("role") or "").casefold()
        if role in {"admin", "system_admin"}:
            return "admin"
        if role in {"domain_owner", "domain_admin"}:
            return "domain_owner"
        return "requester"

    def _build_permissions(self, actor_id: str, role: str, store_ids: list[int] | None) -> Any:
        perm_set = None
        try:
            from chat_gateway.auth_store import load_effective_permissions

            perm_set = load_effective_permissions(actor_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("permission resolve error: %s", exc)
            perm_set = None
        if perm_set is not None:
            return build_permissions_snapshot(
                actor_id,
                role,
                store_ids=store_ids,
                permission_set=perm_set,
                all_tables=self.pipeline.catalog.logical_table_names(),
            )
        # Fail-closed: no capabilities resolvable from the AUTH DB -> deny access.
        # Dev-only convenience: ALLOW_DEV_AUTH falls back to YAML roles so local
        # runs work without an AUTH DB.
        if os.getenv("ALLOW_DEV_AUTH") == "1":
            return build_permissions_snapshot(actor_id, role, store_ids=store_ids)
        raise PermissionsUnavailableError(
            "cannot resolve permissions from AUTH DB (user inactive/absent or DB unavailable)"
        )

    def _session_budget(self, bundle: SessionBundle) -> SessionTraceBudget:
        spent = bundle.workflow.budget_spent if bundle.workflow else {}
        if isinstance(spent, dict) and spent:
            tb = TraceBudget(spent={**TraceBudget().spent, **spent})
            return SessionTraceBudget(tb)
        return SessionTraceBudget()

    def _prepare_context_pack(
        self,
        *,
        bundle: SessionBundle,
        message: str,
        current_turn_id: str,
        external_sources: list[dict[str, Any]],
        invoker: HttpAgentInvoker,
        session_budget: SessionTraceBudget,
        actor_id: str,
        session_id: str,
    ):
        assert bundle.workflow is not None
        cfg = self.cfg.stm.context_pack
        pack, candidates, need_curator = build_context_pack_hard(
            transcript=bundle.transcript,
            workflow=bundle.workflow,
            current_message=message,
            cfg=cfg,
            current_turn_id=current_turn_id,
            external_sources=external_sources,
        )
        if not need_curator:
            return pack

        curator_input = {
            "current_message": message,
            "working_memory": (bundle.workflow.working_memory or WorkingMemory()).model_dump(
                mode="json"
            ),
            "last_resolved_brief": (
                bundle.workflow.last_resolved_brief.model_dump(mode="json")
                if bundle.workflow.last_resolved_brief
                else None
            ),
            "candidates": [c.model_dump(mode="json") for c in candidates],
            "pack_token_budget": cfg.pack_token_budget,
        }
        curator_failed = False
        curator_out: dict[str, Any] = {}
        try:
            # Charge as Agent I; isolated clean-window call
            curator_out = self._invoke_agent_i(
                invoker,
                curator_input,
                {
                    "mode": "context_curator",
                    "session_id": session_id,
                    "actor_id": actor_id,
                    "curator_input": curator_input,
                },
                session_budget,
                bundle,
            )
        except Exception:  # noqa: BLE001
            logger.exception("context_curator failed; falling back to hard-only pack")
            curator_failed = True

        selected = candidates
        archive_id = None
        if not curator_failed and curator_out:
            selected = apply_curator_selection(
                candidates,
                curator_out.get("selected_turn_ids"),
                curator_out.get("drop_turn_ids"),
            )
            bundle.workflow.working_memory = merge_ccs_patch(
                bundle.workflow.working_memory or WorkingMemory(),
                curator_out.get("ccs_patch") if isinstance(curator_out.get("ccs_patch"), dict) else {},
            )
            observations = [str(x) for x in (curator_out.get("observations") or [])][:20]
            summary = curator_out.get("compact_summary")
            if summary or observations or selected:
                entry = CompactArchiveEntry(
                    at=utc_now().isoformat(),
                    reason="curator",
                    summary=str(summary or "")[:1600],
                    selected_turn_ids=[t.id for t in selected],
                    observations=observations,
                    source_turn_ids=[c.id for c in candidates],
                )
                archive_id = append_compact_archive(
                    bundle.workflow, entry, max_entries=cfg.compact_archive_max
                )

        return assemble_context_pack(
            current_message=message,
            workflow=bundle.workflow,
            selected_turns=selected,
            cfg=cfg,
            strategy="curator" if not curator_failed else "curator_failed_hard",
            curator_invoked=True,
            curator_failed=curator_failed,
            archive_id=archive_id,
            pct_before=pack.pack_meta.pct,
            external_sources=external_sources,
            dropped_turns=pack.pack_meta.dropped_turns,
        )

    def _invoke_agent_i(
        self,
        invoker: HttpAgentInvoker,
        payload: dict[str, Any],
        metadata: dict[str, Any],
        budget: SessionTraceBudget,
        bundle: SessionBundle,
    ) -> dict[str, Any]:
        budget.record("I")
        meta = {
            **metadata,
            "session_bundle": {
                "session_id": bundle.session_id,
                "actor_id": bundle.actor_id,
                # Do not dump full L0 into agent metadata; ContextPack is authoritative.
                "transcript_len": len(bundle.transcript),
                "workflow_summary": self.context_policy.build_request_context(
                    "I", bundle.actor_id, bundle
                ).get("workflow_summary", {}),
            },
        }
        out = invoker.invoke("I", payload, meta)
        tokens = int(out.pop("usage_tokens", 0) or 0)
        if tokens:
            budget.trace_budget.charge("tokens", tokens=tokens)
        return out

    def _handle_teach_domain_fact(
        self,
        *,
        session_id: str,
        message: str,
        user: dict[str, Any],
        bundle: SessionBundle,
        ingress: dict[str, Any],
    ) -> ChatResponse:
        raw = ingress.get("domain_fact") or {}
        try:
            payload = DomainFactTeachPayload.model_validate(raw)
        except Exception:  # noqa: BLE001
            payload = DomainFactTeachPayload(statement=str(raw.get("statement") or "").strip())
        statement = (payload.statement or "").strip() or message.strip()
        if not statement:
            ask = ingress.get("user_message") or "Bạn muốn lưu quy tắc nghiệp vụ nào?"
            assistant = TranscriptTurn(
                id=str(uuid4()),
                role="assistant",
                content=ask,
                at=utc_now().isoformat(),
            )
            bundle.transcript.append(assistant)
            self.stm.save_transcript(session_id, bundle.transcript)
            return ChatResponse(
                session_id=session_id,
                workflow_status=WorkflowStatus.IDLE.value,
                message=ask,
            )

        catalog = getattr(self.pipeline, "column_catalog", None) or ColumnSemanticCatalog.from_columns_dir()
        links = normalize_schema_links(payload.schema_links, catalog=catalog)
        if not links:
            # Fallback: try to pick links from statement tokens without inventing SQL.
            hinted: list[dict[str, str]] = []
            upper = statement.upper()
            for bare in ("TRANSHDR", "STRANS", "PMTRANS", "SKU_DEF"):
                if bare in upper:
                    hinted.append({"table": bare})
            if "AMOUNT" in upper and "TRANSHDR" in upper:
                hinted.append({"table": "TRANSHDR", "column": "AMOUNT"})
            if "AMOUNT" in upper and "STRANS" in upper:
                hinted.append({"table": "STRANS", "column": "AMOUNT"})
            if "TRANS_NUM" in upper:
                hinted.append({"table": "TRANSHDR", "column": "TRANS_NUM"})
            links = normalize_schema_links(hinted, catalog=catalog)

        ack_default = (
            "Đã ghi nhận quy tắc nghiệp vụ."
            if links
            else "Đã nhận statement nhưng chưa gắn được schema link rõ ràng — vui lòng nêu bảng/cột."
        )
        user_message = (ingress.get("user_message") or "").strip() or ack_default

        rule_id = ""
        if links and self.domain_rule_store is not None:
            candidate = DomainRuleCandidate(
                statement=statement,
                fact_type=payload.fact_type,
                scope=payload.scope if payload.scope in {"user", "tenant", "global"} else "user",
                schema_links=links,
                confidence=1.0,
                evidence=[
                    DomainEvidence(
                        source_kind="user_statement",
                        source_ref="chat_teach",
                        quote=message,
                        schema_links=links,
                        confidence=1.0,
                    )
                ],
            )
            staged = self.stage_domain_rule(
                candidate,
                trace_id=f"teach:{session_id}:{uuid4()}",
                user=user,
            )
            rule_id = str(staged.get("rule_id") or "")
            if staged.get("status") == "ok" and rule_id:
                status = "candidate"
                if self.domain_rule_store is not None:
                    doc = self.domain_rule_store.collection.find_one({"rule_id": rule_id}) or {}
                    status = str(doc.get("status") or "candidate")
                if status == "confirmed":
                    user_message = (
                        ingress.get("user_message")
                        or f"Đã lưu và xác nhận fact (rule_id={rule_id})."
                    )
                else:
                    user_message = (
                        ingress.get("user_message")
                        or f"Đã đưa fact vào hàng đợi Domain Rules (rule_id={rule_id})."
                    )
            elif staged.get("status") == "no_store":
                user_message = "Hệ thống chưa bật kho domain rules — không lưu được fact."
        elif not links:
            pass
        else:
            user_message = "Hệ thống chưa bật kho domain rules — không lưu được fact."

        assistant = TranscriptTurn(
            id=str(uuid4()),
            role="assistant",
            content=user_message,
            at=utc_now().isoformat(),
        )
        bundle.transcript.append(assistant)
        self.stm.save_transcript(session_id, bundle.transcript)
        return ChatResponse(
            session_id=session_id,
            workflow_status=WorkflowStatus.IDLE.value,
            message=user_message,
            analysis_id=rule_id or None,
        )

    def _handle_satisfaction_signal(self, ingress: dict[str, Any], bundle: SessionBundle) -> None:
        raw = ingress.get("satisfaction_signal")
        if not raw or not self.feedback:
            return
        trace_id = bundle.workflow.last_completed_trace_id if bundle.workflow else None
        if not trace_id:
            return
        signal = SatisfactionSignal(
            applies_to_trace_id=trace_id,
            sentiment=raw.get("sentiment", "unknown"),
            confidence=float(raw.get("confidence", 0)),
            failure_mode=raw.get("intent"),
            evidence=raw.get("evidence", ""),
        )
        self.feedback.on_satisfaction_signal(signal)

    def _maybe_emit_re_ask_signal(self, session_id: str, bundle: SessionBundle, message: str) -> None:
        wf = bundle.workflow
        if not wf or not self.feedback:
            return
        if wf.last_outcome not in _NEGATIVE_OUTCOMES:
            return
        if not wf.last_completed_trace_id:
            return
        prev_intent = (wf.brief.intent if wf.brief else "") or ""
        if prev_intent and message.strip().lower()[:40] in prev_intent.lower()[:80]:
            self.feedback.on_behavioral_signal(
                session_id,
                BehavioralSignal(
                    session_id=session_id,
                    signal_type="re_ask",
                    trace_id=wf.last_completed_trace_id,
                    weight=0.4,
                ),
            )

    def _refresh_workflow_staleness(self, session_id: str, bundle: SessionBundle) -> None:
        wf = bundle.workflow
        if wf is None or wf.status != WorkflowStatus.AWAITING_CLARIFICATION:
            return
        age = (utc_now() - wf.updated_at).total_seconds()
        if age <= self.cfg.pipeline.workflow_stale_ttl_seconds:
            return
        wf.status = WorkflowStatus.STALE
        self.stm.save_clarification(session_id, None)
        self.stm.save_workflow(session_id, wf)

    def _handle_confirm_cancel(
        self,
        session_id: str,
        bundle: SessionBundle,
        ingress: dict[str, Any],
    ) -> ChatResponse:
        token = self._cancel_tokens.get(session_id)
        if token is not None:
            token.cancel()
        wf = bundle.workflow
        if wf is None:
            return ChatResponse(
                session_id=session_id,
                workflow_status=WorkflowStatus.IDLE.value,
                message=ingress.get("user_message", "Đã hủy."),
            )
        if wf.status == WorkflowStatus.RUNNING:
            mark_cancelled(wf)
        else:
            wf.status = WorkflowStatus.IDLE
        wf.pending_clarification = None
        wf.progress_step = None
        self.stm.save_clarification(session_id, None)
        self.stm.save_workflow(session_id, wf)
        msg = ingress.get("user_message", "Đã hủy phân tích.")
        assistant = TranscriptTurn(
            id=str(uuid4()),
            role="assistant",
            content=msg,
            at=utc_now().isoformat(),
        )
        bundle.transcript.append(assistant)
        self.stm.save_transcript(session_id, bundle.transcript)
        return ChatResponse(
            session_id=session_id,
            workflow_status=wf.status.value,
            outcome=AnalysisOutcome.CANCELLED.value if wf.status == WorkflowStatus.CANCELLED else None,
            message=msg,
        )

    def _maybe_rephrase_retry(
        self,
        *,
        session_id: str,
        ingress: dict[str, Any],
        bundle: SessionBundle,
        permissions: Any,
        invoker: HttpAgentInvoker,
        session_budget: SessionTraceBudget,
    ) -> ChatResponse | None:
        raw = ingress.get("satisfaction_signal") or {}
        if raw.get("intent") != "rephrase_retry":
            return None
        wf = bundle.workflow
        if wf is None or not wf.brief:
            return None
        analysis_id = wf.active_analysis_id or wf.last_completed_trace_id or str(uuid4())
        resume_analysis(wf)
        wf.brief = AnalysisBrief.model_validate(wf.brief.model_dump())
        self.stm.save_workflow(session_id, wf)
        self._cancel_tokens[session_id] = CancellationToken()
        return self._run_pipeline_and_respond(
            session_id=session_id,
            analysis_id=analysis_id,
            brief=wf.brief,
            bundle=bundle,
            permissions=permissions,
            invoker=invoker,
            session_budget=session_budget,
        )

    def _resume_from_pending_clarification(
        self,
        *,
        session_id: str,
        message: str,
        user: dict[str, Any],
        bundle: SessionBundle,
    ) -> ChatResponse:
        invoker = self._make_invoker()
        session_budget = self._session_budget(bundle)
        request = ClarificationRequest.model_validate(bundle.clarification)
        try:
            pack = self._prepare_context_pack(
                bundle=bundle,
                message=message,
                current_turn_id="clarify-current",
                external_sources=[],
                invoker=invoker,
                session_budget=session_budget,
                actor_id=user["sub"],
                session_id=session_id,
            )
            bridge = self._invoke_agent_i(
                invoker,
                {},
                {
                    "mode": "clarification_bridge",
                    "session_id": session_id,
                    "actor_id": user["sub"],
                    "clarification_request": request.model_dump(),
                    "context_pack": pack.to_ingress_user_content(),
                },
                session_budget,
                bundle,
            )
        except BudgetExceededError as exc:
            return ChatResponse(
                session_id=session_id,
                workflow_status=bundle.workflow.status.value if bundle.workflow else "idle",
                message=str(exc),
                error={"code": "BUDGET_EXCEEDED", "retryable": False},
            )

        brief = bundle.workflow.brief or request.partial_brief
        analysis_id = bundle.workflow.active_analysis_id or str(uuid4())
        if bridge.get("action") == "resolve_from_transcript":
            reply = ClarificationReply(analysis_id=analysis_id, answers=bridge.get("answers") or [])
            brief = apply_clarification_reply(brief, reply, request)
        else:
            brief.exploration_mode = True
            brief.user_knowledge_level = "unknown"

        bundle.workflow.brief = brief
        resume_analysis(bundle.workflow)
        self.stm.save_clarification(session_id, None)
        self.stm.save_workflow(session_id, bundle.workflow)
        permissions = bundle.workflow.permissions_snapshot or self._build_permissions(*claims_from_user_dict(user))
        return self._run_pipeline_and_respond(
            session_id=session_id,
            analysis_id=analysis_id,
            brief=brief,
            bundle=bundle,
            permissions=permissions,
            invoker=invoker,
            session_budget=session_budget,
        )

    def _run_pipeline_and_respond(
        self,
        *,
        session_id: str,
        analysis_id: str,
        brief: AnalysisBrief,
        bundle: SessionBundle,
        permissions: Any,
        invoker: HttpAgentInvoker,
        session_budget: SessionTraceBudget,
    ) -> ChatResponse:
        def on_progress(workflow: Any) -> None:
            self.stm.save_workflow(session_id, workflow)
            for sink in list(self.progress_sinks):
                try:
                    sink(workflow)
                except Exception:
                    logger.exception("progress sink failed for session %s", session_id)

        deadline = time.monotonic() + float(self.cfg.pipeline.max_sync_seconds)
        cancel_token = self._cancel_tokens.get(session_id)
        progress_cb = on_progress if (self.cfg.pipeline.poll_enabled or self.progress_sinks) else None
        try:
            result = self.pipeline.run(
                brief=brief,
                workflow=bundle.workflow,
                permissions=permissions,
                trace_budget=session_budget.trace_budget,
                on_progress=progress_cb,
                deadline=deadline,
                cancel_token=cancel_token,
            )
        except ClarifyRoundsExceededError as exc:
            brief.exploration_mode = True
            brief.user_knowledge_level = "unknown"
            bundle.workflow.brief = brief
            resume_analysis(bundle.workflow)
            self.stm.save_workflow(session_id, bundle.workflow)
            try:
                result = self.pipeline.run(
                    brief=brief,
                    workflow=bundle.workflow,
                    permissions=permissions,
                    trace_budget=session_budget.trace_budget,
                    on_progress=progress_cb,
                    deadline=deadline,
                    cancel_token=cancel_token,
                )
            except ClarifyRoundsExceededError:
                return ChatResponse(
                    session_id=session_id,
                    analysis_id=analysis_id,
                    workflow_status=WorkflowStatus.STALE.value,
                    outcome="error",
                    message=str(exc),
                    error={"code": "CLARIFY_ROUNDS_EXCEEDED", "retryable": False},
                )
        except BudgetExceededError as exc:
            bundle.workflow.budget_spent = session_budget.trace_budget.spent
            self.stm.save_workflow(session_id, bundle.workflow)
            return ChatResponse(
                session_id=session_id,
                analysis_id=analysis_id,
                workflow_status=bundle.workflow.status.value,
                outcome="error",
                message=str(exc),
                error={"code": "BUDGET_EXCEEDED", "retryable": False},
            )

        bundle.workflow.budget_spent = session_budget.trace_budget.spent

        if result.needs_clarification:
            return self._handle_clarification_needed(
                session_id=session_id,
                analysis_id=analysis_id,
                result=result,
                brief=brief,
                bundle=bundle,
                permissions=permissions,
                invoker=invoker,
                session_budget=session_budget,
            )

        try:
            synth = self._invoke_agent_i(
                invoker,
                {},
                {
                    "mode": "synthesize",
                    "session_id": session_id,
                    "actor_id": permissions.actor_id,
                    "technical_summary": result.technical_summary.model_dump(),
                },
                session_budget,
                bundle,
            )
        except BudgetExceededError:
            bundle.workflow.budget_spent = session_budget.trace_budget.spent
            self.stm.save_workflow(session_id, bundle.workflow)
            return ChatResponse(
                session_id=session_id,
                analysis_id=analysis_id,
                trace_id=result.trace_id,
                workflow_status=bundle.workflow.status.value,
                outcome=result.outcome,
                message=result.technical_summary.outcome,
                error={"code": "BUDGET_EXCEEDED", "retryable": False},
            )

        assistant_text = str(synth.get("user_message") or "").strip()
        artifact_urls = list(result.technical_summary.artifact_urls or [])
        public_artifacts: list[dict[str, str]] = []
        file_names: list[str] = []
        for raw in artifact_urls:
            path = Path(str(raw))
            name = path.name or "artifact"
            file_names.append(name)
            public_artifacts.append(
                {"url": f"/artifacts/{result.trace_id}/{name}", "name": name}
            )
        metrics = result.technical_summary.headline_metrics or {}
        sheet_rows = metrics.get("artifact_rows")
        if isinstance(sheet_rows, dict) and sheet_rows:
            parts = [
                f"{str(key).split(':')[-1]}: {value} dòng"
                for key, value in sheet_rows.items()
            ]
            sheet_note = "Kết quả gồm " + "; ".join(parts) + "."
            if sheet_note.lower() not in assistant_text.lower():
                assistant_text = f"{assistant_text} {sheet_note}".strip()
        if file_names and "tải" not in assistant_text.lower() and "file" not in assistant_text.lower():
            assistant_text = (
                f"{assistant_text} File đính kèm sẵn sàng tải: {', '.join(file_names)}."
            ).strip()

        assistant = TranscriptTurn(
            id=str(uuid4()),
            role="assistant",
            content=assistant_text,
            at=utc_now().isoformat(),
            analysis_id=analysis_id,
            trace_id=result.trace_id,
        )
        bundle.transcript.append(assistant)
        self.stm.save_transcript(session_id, bundle.transcript)
        # Persist L4 + refresh L2 on success/empty only
        if result.outcome in {
            AnalysisOutcome.SUCCESS.value,
            AnalysisOutcome.EMPTY.value,
            "success",
            "empty",
        }:
            bundle.workflow.last_resolved_brief = brief
            bundle.workflow.working_memory = refresh_working_memory_from_brief(
                brief, bundle.workflow.working_memory
            )
        self.stm.save_workflow(session_id, bundle.workflow)
        return ChatResponse(
            session_id=session_id,
            analysis_id=analysis_id,
            trace_id=result.trace_id,
            workflow_status=bundle.workflow.status.value,
            outcome=result.outcome,
            message=assistant_text,
            artifacts=public_artifacts,
        )

    def _handle_clarification_needed(
        self,
        *,
        session_id: str,
        analysis_id: str,
        result: Any,
        brief: AnalysisBrief,
        bundle: SessionBundle,
        permissions: Any,
        invoker: HttpAgentInvoker,
        session_budget: SessionTraceBudget,
    ) -> ChatResponse:
        assert result.needs_clarification is not None
        try:
            pack = self._prepare_context_pack(
                bundle=bundle,
                message="",
                current_turn_id="pipeline-clarify",
                external_sources=[],
                invoker=invoker,
                session_budget=session_budget,
                actor_id=permissions.actor_id,
                session_id=session_id,
            )
            bridge = self._invoke_agent_i(
                invoker,
                {},
                {
                    "mode": "clarification_bridge",
                    "session_id": session_id,
                    "actor_id": permissions.actor_id,
                    "clarification_request": result.needs_clarification.model_dump(),
                    "context_pack": pack.to_ingress_user_content(),
                },
                session_budget,
                bundle,
            )
        except BudgetExceededError as exc:
            bundle.workflow.budget_spent = session_budget.trace_budget.spent
            self.stm.save_workflow(session_id, bundle.workflow)
            return ChatResponse(
                session_id=session_id,
                analysis_id=analysis_id,
                trace_id=result.trace_id,
                workflow_status=WorkflowStatus.AWAITING_CLARIFICATION.value,
                outcome=result.outcome,
                message=str(exc),
                error={"code": "BUDGET_EXCEEDED", "retryable": False},
            )

        if bridge.get("action") == "resolve_from_transcript":
            brief, should_rerun = self.clarify.on_pipeline_clarify(
                result=result,
                brief=brief,
                bridge=bridge,
                analysis_id=analysis_id,
            )
            if should_rerun:
                bundle.workflow.brief = brief
                resume_analysis(bundle.workflow)
                bundle.workflow.budget_spent = session_budget.trace_budget.spent
                self.stm.save_workflow(session_id, bundle.workflow)
                return self._run_pipeline_and_respond(
                    session_id=session_id,
                    analysis_id=analysis_id,
                    brief=brief,
                    bundle=bundle,
                    permissions=permissions,
                    invoker=invoker,
                    session_budget=session_budget,
                )

        try:
            clarify = self._invoke_agent_i(
                invoker,
                {},
                {
                    "mode": "clarify",
                    "session_id": session_id,
                    "actor_id": permissions.actor_id,
                    "clarification_request": result.needs_clarification.model_dump(),
                },
                session_budget,
                bundle,
            )
        except BudgetExceededError as exc:
            bundle.workflow.budget_spent = session_budget.trace_budget.spent
            self.stm.save_workflow(session_id, bundle.workflow)
            return ChatResponse(
                session_id=session_id,
                analysis_id=analysis_id,
                trace_id=result.trace_id,
                workflow_status=WorkflowStatus.AWAITING_CLARIFICATION.value,
                outcome=result.outcome,
                message=str(exc),
                error={"code": "BUDGET_EXCEEDED", "retryable": False},
            )

        bundle.workflow.budget_spent = session_budget.trace_budget.spent
        self.stm.save_clarification(session_id, result.needs_clarification.model_dump())
        self.stm.save_workflow(session_id, bundle.workflow)
        return self.clarify.suspend_response(
            session_id=session_id,
            analysis_id=analysis_id,
            request=result.needs_clarification,
            clarify_payload=clarify,
            workflow_status=WorkflowStatus.AWAITING_CLARIFICATION.value,
        ).model_copy(
            update={
                "trace_id": result.trace_id,
                "outcome": result.outcome,
                "bridge_action": "ask_user",
            }
        )
