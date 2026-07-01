from __future__ import annotations

import os
from datetime import datetime
from typing import Any
from uuid import uuid4

from project_core.config.loader import load_project_config
from project_core.domain.access.acl import build_permissions_snapshot
from project_core.domain.clarification.resolver import apply_clarification_reply
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import ClarificationReply, ClarificationRequest
from project_core.domain.contracts.pipeline import ChatResponse
from project_core.domain.contracts.workflow import WorkflowStatus
from project_core.domain.errors.codes import ClarifyRoundsExceededError
from project_core.domain.feedback.analysis_tool_registry import AnalysisToolRegistry
from project_core.domain.feedback.domain_rule_store import DomainRuleStore
from project_core.domain.feedback.loop import CaseStudyIndexer, FeedbackLoop
from project_core.domain.retrieval.mongo_vector import MongoVectorRetriever
from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.workflow.state import new_workflow, resume_analysis, start_analysis
from project_core.infra.stm.redis_store import RedisSessionStore
from project_core.domain.memory.session_bundle import TranscriptTurn
from project_core.orchestration.pipeline import SupermarketAnalysisPipeline

from chat_gateway.clients import HttpAgentInvoker, HttpSqlGatewayClient


class ChatOrchestrator:
    def __init__(self) -> None:
        self.stm = RedisSessionStore()
        self.cfg = load_project_config()
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

            retriever = MongoVectorRetriever(db)
            self.analysis_tool_registry = AnalysisToolRegistry(db["analysis_tools"], embed_fn=_embed_text)
            set_registry(self.analysis_tool_registry)
            self.domain_rule_store = DomainRuleStore(db["domain_rules"])
            self.feedback = FeedbackLoop(indexer=indexer, retriever=retriever, embed_fn=_embed_text)
        except Exception:  # noqa: BLE001
            pass
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

        turn = TranscriptTurn(id=str(uuid4()), role="user", content=message, at=datetime.utcnow().isoformat())
        bundle.transcript.append(turn)
        self.stm.save_transcript(session_id, bundle.transcript)

        invoker = HttpAgentInvoker()
        external_sources = []
        if bundle.workflow.brief and bundle.workflow.brief.external_sources:
            external_sources = [s.model_dump() for s in bundle.workflow.brief.external_sources]

        ingress = invoker.invoke(
            "I",
            {"text": message, "external_sources": external_sources},
            {"mode": "ingress", "session_id": session_id, "actor_id": actor_id},
        )
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
        permissions = build_permissions_snapshot(actor_id, role, store_ids=store_ids)
        bundle.workflow.permissions_snapshot = permissions
        self.stm.save_workflow(session_id, bundle.workflow)

        return self._run_pipeline_and_respond(
            session_id=session_id,
            analysis_id=analysis_id,
            brief=brief,
            bundle=bundle,
            permissions=permissions,
            invoker=invoker,
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

        permissions = bundle.workflow.permissions_snapshot or build_permissions_snapshot(
            user["sub"], user.get("role", "hq_analyst"), store_ids=user.get("store_ids")
        )
        invoker = HttpAgentInvoker()
        return self._run_pipeline_and_respond(
            session_id=session_id,
            analysis_id=reply.analysis_id,
            brief=brief,
            bundle=bundle,
            permissions=permissions,
            invoker=invoker,
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

    def _resume_from_pending_clarification(
        self,
        *,
        session_id: str,
        message: str,
        user: dict[str, Any],
        bundle: Any,
    ) -> ChatResponse:
        invoker = HttpAgentInvoker()
        request = ClarificationRequest.model_validate(bundle.clarification)
        bridge = invoker.invoke(
            "I",
            {},
            {
                "mode": "clarification_bridge",
                "session_id": session_id,
                "actor_id": user["sub"],
                "clarification_request": request.model_dump(),
                "transcript": [t.model_dump() for t in bundle.transcript] + [
                    {"id": str(uuid4()), "role": "user", "content": message, "at": datetime.utcnow().isoformat()}
                ],
            },
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
        permissions = bundle.workflow.permissions_snapshot or build_permissions_snapshot(
            user["sub"], user.get("role", "hq_analyst"), store_ids=user.get("store_ids")
        )
        return self._run_pipeline_and_respond(
            session_id=session_id,
            analysis_id=analysis_id,
            brief=brief,
            bundle=bundle,
            permissions=permissions,
            invoker=invoker,
        )

    def _run_pipeline_and_respond(
        self,
        *,
        session_id: str,
        analysis_id: str,
        brief: AnalysisBrief,
        bundle: Any,
        permissions: Any,
        invoker: HttpAgentInvoker,
    ) -> ChatResponse:
        try:
            result = self.pipeline.run(brief=brief, workflow=bundle.workflow, permissions=permissions)
        except ClarifyRoundsExceededError as exc:
            brief.exploration_mode = True
            brief.user_knowledge_level = "unknown"
            bundle.workflow.brief = brief
            resume_analysis(bundle.workflow)
            self.stm.save_workflow(session_id, bundle.workflow)
            try:
                result = self.pipeline.run(brief=brief, workflow=bundle.workflow, permissions=permissions)
            except ClarifyRoundsExceededError:
                return ChatResponse(
                    session_id=session_id,
                    analysis_id=analysis_id,
                    workflow_status=WorkflowStatus.STALE.value,
                    outcome="error",
                    message=str(exc),
                    error={"code": "CLARIFY_ROUNDS_EXCEEDED", "retryable": False},
                )

        if result.needs_clarification:
            return self._handle_clarification_needed(
                session_id=session_id,
                analysis_id=analysis_id,
                result=result,
                brief=brief,
                bundle=bundle,
                permissions=permissions,
                invoker=invoker,
            )

        synth = invoker.invoke(
            "I",
            {},
            {
                "mode": "synthesize",
                "session_id": session_id,
                "actor_id": permissions.actor_id,
                "technical_summary": result.technical_summary.model_dump(),
            },
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
        bundle: Any,
        permissions: Any,
        invoker: HttpAgentInvoker,
    ) -> ChatResponse:
        assert result.needs_clarification is not None
        bridge = invoker.invoke(
            "I",
            {},
            {
                "mode": "clarification_bridge",
                "session_id": session_id,
                "actor_id": permissions.actor_id,
                "clarification_request": result.needs_clarification.model_dump(),
                "transcript": [t.model_dump() for t in bundle.transcript],
            },
        )
        if bridge.get("action") == "resolve_from_transcript":
            reply = ClarificationReply(analysis_id=analysis_id, answers=bridge.get("answers") or [])
            brief = apply_clarification_reply(brief, reply, result.needs_clarification)
            bundle.workflow.brief = brief
            resume_analysis(bundle.workflow)
            self.stm.save_workflow(session_id, bundle.workflow)
            return self._run_pipeline_and_respond(
                session_id=session_id,
                analysis_id=analysis_id,
                brief=brief,
                bundle=bundle,
                permissions=permissions,
                invoker=invoker,
            )

        clarify = invoker.invoke(
            "I",
            {},
            {
                "mode": "clarify",
                "session_id": session_id,
                "actor_id": permissions.actor_id,
                "clarification_request": result.needs_clarification.model_dump(),
            },
        )
        self.stm.save_clarification(session_id, result.needs_clarification.model_dump())
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
