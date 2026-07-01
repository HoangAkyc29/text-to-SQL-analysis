from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any
from uuid import uuid4

from project_core.config.loader import load_project_config
from project_core.domain.access.acl import build_permissions_snapshot
from project_core.domain.access.context_policy import ContextPolicy
from project_core.domain.budget import SessionTraceBudget, TraceBudget
from project_core.domain.clarification.resolver import apply_clarification_reply
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import ClarificationReply, ClarificationRequest
from project_core.domain.contracts.feedback import SatisfactionSignal
from project_core.domain.contracts.pipeline import ChatResponse
from project_core.domain.contracts.workflow import WorkflowStatus
from project_core.domain.errors.codes import BudgetExceededError, ClarifyRoundsExceededError
from project_core.domain.feedback.analysis_tool_registry import AnalysisToolRegistry
from project_core.domain.feedback.domain_rule_store import DomainRuleStore
from project_core.domain.feedback.loop import CaseStudyIndexer, FeedbackLoop
from project_core.domain.feedback.store import BehavioralSignal
from project_core.domain.memory.session_bundle import SessionBundle, TranscriptTurn
from project_core.domain.retrieval.mongo_vector import HybridMongoRetriever, MongoVectorRetriever
from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.workflow.state import new_workflow, resume_analysis, start_analysis
from project_core.infra.stm.redis_store import RedisSessionStore
from project_core.orchestration.pipeline import SupermarketAnalysisPipeline

from chat_gateway.clients import HttpAgentInvoker, HttpSqlGatewayClient

logger = logging.getLogger(__name__)

_NEGATIVE_OUTCOMES = frozenset({"error", "impossible", "policy_blocked", "partial"})


class ChatOrchestrator:
    def __init__(self) -> None:
        self.stm = RedisSessionStore()
        self.cfg = load_project_config()
        self.context_policy = ContextPolicy()
        self.feedback: FeedbackLoop | None = None
        self.analysis_tool_registry: AnalysisToolRegistry | None = None
        self.domain_rule_store: DomainRuleStore | None = None
        try:
            from pymongo import MongoClient

            from project_core.domain.analysis.recipe_runtime import set_registry
            from project_core.llm.embedding_client import EmbeddingClient

            mongo = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/supermarket_agent"))
            db = mongo.get_default_database()
            indexer = CaseStudyIndexer(db["case_studies"])

            def _embed_text(text: str) -> list[float]:
                return EmbeddingClient().embed([text])[0]

            retriever = HybridMongoRetriever(db)
            self.analysis_tool_registry = AnalysisToolRegistry(db["analysis_tools"], embed_fn=_embed_text)
            set_registry(self.analysis_tool_registry)
            self.domain_rule_store = DomainRuleStore(db["domain_rules"])
            self.feedback = FeedbackLoop(indexer=indexer, retriever=retriever, embed_fn=_embed_text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Mongo/RAG unavailable: %s", exc)
        self.pipeline = SupermarketAnalysisPipeline(
            agent_invoker=HttpAgentInvoker(),
            sql_gateway=HttpSqlGatewayClient(),
            catalog=SchemaCatalog.from_dictionary_dir(),
            feedback_loop=self.feedback,
            analysis_tool_registry=self.analysis_tool_registry,
            domain_rule_store=self.domain_rule_store,
        )

    def handle_chat(self, *, session_id: str, message: str, user: dict[str, Any]) -> ChatResponse:
        actor_id = user["sub"]
        role = user.get("role", "hq_analyst")
        store_ids = user.get("store_ids")
        bundle = self.stm.load_session(session_id)
        if bundle.workflow is None:
            bundle.workflow = new_workflow(session_id, actor_id)

        if bundle.workflow.status == WorkflowStatus.AWAITING_CLARIFICATION and bundle.clarification:
            return self._resume_from_pending_clarification(
                session_id=session_id,
                message=message,
                user=user,
                bundle=bundle,
            )

        self._maybe_emit_re_ask_signal(session_id, bundle, message)

        turn = TranscriptTurn(id=str(uuid4()), role="user", content=message, at=datetime.utcnow().isoformat())
        bundle.transcript.append(turn)
        self.stm.save_transcript(session_id, bundle.transcript)

        invoker = HttpAgentInvoker()
        session_budget = self._session_budget(bundle)
        external_sources = []
        if bundle.workflow.brief and bundle.workflow.brief.external_sources:
            external_sources = [s.model_dump() for s in bundle.workflow.brief.external_sources]

        try:
            ingress = self._invoke_agent_i(
                invoker,
                {"text": message, "external_sources": external_sources},
                {"mode": "ingress", "session_id": session_id, "actor_id": actor_id},
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

        if ingress.get("route") != "analysis":
            assistant = TranscriptTurn(
                id=str(uuid4()),
                role="assistant",
                content=ingress.get("user_message", ""),
                at=datetime.utcnow().isoformat(),
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
        brief = apply_clarification_reply(brief, reply, request)
        bundle.workflow.brief = brief
        resume_analysis(bundle.workflow)
        self.stm.save_clarification(session_id, None)
        self.stm.save_workflow(session_id, bundle.workflow)

        permissions = bundle.workflow.permissions_snapshot or self._build_permissions(
            user["sub"], user.get("role", "hq_analyst"), user.get("store_ids")
        )
        invoker = HttpAgentInvoker()
        session_budget = self._session_budget(bundle)
        return self._run_pipeline_and_respond(
            session_id=session_id,
            analysis_id=reply.analysis_id,
            brief=brief,
            bundle=bundle,
            permissions=permissions,
            invoker=invoker,
            session_budget=session_budget,
        )

    def confirm_domain_rule(self, rule_id: str, *, confirmed: bool, user: dict[str, Any]) -> dict[str, str]:
        if self.domain_rule_store is None:
            return {"status": "no_store"}
        if confirmed:
            self.domain_rule_store.confirm(rule_id, confirmed_by=user["sub"])
        else:
            self.domain_rule_store.reject(rule_id)
        return {"status": "ok"}

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

    def analysis_status(self, analysis_id: str) -> dict[str, Any]:
        found = self.stm.find_by_analysis_id(analysis_id)
        if not found:
            return {"analysis_id": analysis_id, "status": "not_found"}
        session_id, workflow = found
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

    def _build_permissions(self, actor_id: str, role: str, store_ids: list[int] | None) -> Any:
        permissions = build_permissions_snapshot(actor_id, role, store_ids=store_ids)
        grants = set(permissions.tool_grants)
        for agent in ("II", "III", "IV"):
            grants.update(self.context_policy.allowed_mcp_tools(agent))
        permissions.tool_grants = sorted(grants)
        return permissions

    def _session_budget(self, bundle: SessionBundle) -> SessionTraceBudget:
        spent = bundle.workflow.budget_spent if bundle.workflow else {}
        if isinstance(spent, dict) and spent:
            tb = TraceBudget(spent={**TraceBudget().spent, **spent})
            return SessionTraceBudget(tb)
        return SessionTraceBudget()

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
                "transcript": [t.model_dump() for t in bundle.transcript],
                "workflow_summary": self.context_policy.build_request_context(
                    "I", bundle.actor_id, bundle
                ).get("workflow_summary", {}),
            },
        }
        return invoker.invoke("I", payload, meta)

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

    def _resume_from_pending_clarification(
        self,
        *,
        session_id: str,
        message: str,
        user: dict[str, Any],
        bundle: SessionBundle,
    ) -> ChatResponse:
        invoker = HttpAgentInvoker()
        session_budget = self._session_budget(bundle)
        request = ClarificationRequest.model_validate(bundle.clarification)
        try:
            bridge = self._invoke_agent_i(
                invoker,
                {},
                {
                    "mode": "clarification_bridge",
                    "session_id": session_id,
                    "actor_id": user["sub"],
                    "clarification_request": request.model_dump(),
                    "transcript": [t.model_dump() for t in bundle.transcript]
                    + [
                        {
                            "id": str(uuid4()),
                            "role": "user",
                            "content": message,
                            "at": datetime.utcnow().isoformat(),
                        }
                    ],
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
        permissions = bundle.workflow.permissions_snapshot or self._build_permissions(
            user["sub"], user.get("role", "hq_analyst"), user.get("store_ids")
        )
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

        try:
            result = self.pipeline.run(
                brief=brief,
                workflow=bundle.workflow,
                permissions=permissions,
                trace_budget=session_budget.trace_budget,
                on_progress=on_progress if self.cfg.pipeline.poll_enabled else None,
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
                    on_progress=on_progress if self.cfg.pipeline.poll_enabled else None,
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
        except BudgetExceededError as exc:
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

        assistant = TranscriptTurn(
            id=str(uuid4()),
            role="assistant",
            content=synth.get("user_message", ""),
            at=datetime.utcnow().isoformat(),
            analysis_id=analysis_id,
            trace_id=result.trace_id,
        )
        bundle.transcript.append(assistant)
        self.stm.save_transcript(session_id, bundle.transcript)
        self.stm.save_workflow(session_id, bundle.workflow)
        return ChatResponse(
            session_id=session_id,
            analysis_id=analysis_id,
            trace_id=result.trace_id,
            workflow_status=bundle.workflow.status.value,
            outcome=result.outcome,
            message=synth.get("user_message", ""),
            artifacts=[{"url": u} for u in result.technical_summary.artifact_urls],
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
            bridge = self._invoke_agent_i(
                invoker,
                {},
                {
                    "mode": "clarification_bridge",
                    "session_id": session_id,
                    "actor_id": permissions.actor_id,
                    "clarification_request": result.needs_clarification.model_dump(),
                    "transcript": [t.model_dump() for t in bundle.transcript],
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
            reply = ClarificationReply(analysis_id=analysis_id, answers=bridge.get("answers") or [])
            brief = apply_clarification_reply(brief, reply, result.needs_clarification)
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
        suspend_msg = result.needs_clarification.evidence_summary or clarify.get("user_message", "")
        return ChatResponse(
            session_id=session_id,
            analysis_id=analysis_id,
            trace_id=result.trace_id,
            workflow_status=WorkflowStatus.AWAITING_CLARIFICATION.value,
            outcome=result.outcome,
            message=suspend_msg or clarify.get("user_message", ""),
            bridge_action="ask_user",
            clarification=result.needs_clarification,
        )
