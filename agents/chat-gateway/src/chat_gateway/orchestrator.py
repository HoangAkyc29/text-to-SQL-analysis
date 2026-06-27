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
from project_core.domain.feedback.loop import CaseStudyIndexer, FeedbackLoop
from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.workflow.state import new_workflow, start_analysis
from project_core.infra.stm.redis_store import RedisSessionStore
from project_core.domain.memory.session_bundle import TranscriptTurn
from project_core.orchestration.pipeline import SupermarketAnalysisPipeline

from chat_gateway.clients import HttpAgentInvoker, HttpSqlGatewayClient


class ChatOrchestrator:
    def __init__(self) -> None:
        self.stm = RedisSessionStore()
        self.cfg = load_project_config()
        mongo = None
        try:
            from pymongo import MongoClient

            mongo = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/supermarket_agent"))
            db = mongo.get_default_database()
            indexer = CaseStudyIndexer(db["case_studies"])
            self.feedback = FeedbackLoop(indexer=indexer)
        except Exception:  # noqa: BLE001
            self.feedback = None
        self.pipeline = SupermarketAnalysisPipeline(
            agent_invoker=HttpAgentInvoker(),
            sql_gateway=HttpSqlGatewayClient(),
            catalog=SchemaCatalog.from_dictionary_dir(),
            feedback_loop=self.feedback,
        )

    def handle_chat(self, *, session_id: str, message: str, user: dict[str, Any]) -> ChatResponse:
        actor_id = user["sub"]
        role = user.get("role", "hq_analyst")
        store_ids = user.get("store_ids")
        bundle = self.stm.load_session(session_id)
        if bundle.workflow is None:
            bundle.workflow = new_workflow(session_id, actor_id)
        turn = TranscriptTurn(id=str(uuid4()), role="user", content=message, at=datetime.utcnow().isoformat())
        bundle.transcript.append(turn)
        self.stm.save_transcript(session_id, bundle.transcript)

        invoker = HttpAgentInvoker()
        ingress = invoker.invoke(
            "I",
            {"text": message},
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
        analysis_id = start_analysis(bundle.workflow)
        bundle.workflow.brief = brief
        permissions = build_permissions_snapshot(actor_id, role, store_ids=store_ids)
        bundle.workflow.permissions_snapshot = permissions
        self.stm.save_workflow(session_id, bundle.workflow)

        try:
            result = self.pipeline.run(brief=brief, workflow=bundle.workflow, permissions=permissions)
        except ClarifyRoundsExceededError as exc:
            return ChatResponse(
                session_id=session_id,
                analysis_id=analysis_id,
                workflow_status=WorkflowStatus.STALE.value,
                outcome="error",
                message=str(exc),
                error={"code": "CLARIFY_ROUNDS_EXCEEDED", "retryable": False},
            )

        if result.needs_clarification:
            bridge = invoker.invoke(
                "I",
                {},
                {
                    "mode": "clarification_bridge",
                    "session_id": session_id,
                    "actor_id": actor_id,
                    "clarification_request": result.needs_clarification.model_dump(),
                    "transcript": [t.model_dump() for t in bundle.transcript],
                },
            )
            if bridge.get("action") == "resolve_from_transcript":
                reply = ClarificationReply(analysis_id=analysis_id, answers=bridge.get("answers") or [])
                brief = apply_clarification_reply(brief, reply, result.needs_clarification)
                bundle.workflow.brief = brief
                self.stm.save_workflow(session_id, bundle.workflow)
                result = self.pipeline.run(brief=brief, workflow=bundle.workflow, permissions=permissions)
            else:
                clarify = invoker.invoke(
                    "I",
                    {},
                    {
                        "mode": "clarify",
                        "session_id": session_id,
                        "actor_id": actor_id,
                        "clarification_request": result.needs_clarification.model_dump(),
                    },
                )
                self.stm.save_clarification(session_id, result.needs_clarification.model_dump())
                return ChatResponse(
                    session_id=session_id,
                    analysis_id=analysis_id,
                    trace_id=result.trace_id,
                    workflow_status=WorkflowStatus.AWAITING_CLARIFICATION.value,
                    outcome=result.outcome,
                    message=clarify.get("user_message", ""),
                    bridge_action="ask_user",
                    clarification=result.needs_clarification,
                )

        synth = invoker.invoke(
            "I",
            {},
            {
                "mode": "synthesize",
                "session_id": session_id,
                "actor_id": actor_id,
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
