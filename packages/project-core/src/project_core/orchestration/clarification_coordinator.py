from __future__ import annotations

from typing import Any

from project_core.domain.clarification.bridge import ClarificationBridge
from project_core.domain.clarification.resolver import apply_clarification_reply
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import ClarificationReply, ClarificationRequest
from project_core.domain.contracts.pipeline import ChatResponse, PipelineResult
from project_core.domain.memory.session_bundle import SessionBundle, TranscriptTurn


class ClarificationCoordinator:
    """Single entry point for clarification state transitions."""

    def __init__(self, bridge: ClarificationBridge | None = None) -> None:
        self.bridge = bridge or ClarificationBridge()

    def on_ingress_clarify(self, bundle: SessionBundle) -> bool:
        wf = bundle.workflow
        return bool(wf and wf.status.value == "awaiting_clarification" and bundle.clarification)

    def on_resume_reply(
        self,
        *,
        request: ClarificationRequest,
        transcript: list[TranscriptTurn],
        user_message: str,
    ) -> dict[str, Any]:
        extended = transcript + [
            TranscriptTurn(id="resume", role="user", content=user_message, at="now"),
        ]
        return self.bridge.from_transcript_heuristic(request, extended).model_dump()

    def on_bridge_result(
        self,
        *,
        request: ClarificationRequest,
        brief: AnalysisBrief,
        bridge: dict[str, Any],
        analysis_id: str,
    ) -> AnalysisBrief:
        if bridge.get("action") == "resolve_from_transcript":
            reply = ClarificationReply(analysis_id=analysis_id, answers=bridge.get("answers") or [])
            return apply_clarification_reply(brief, reply, request)
        brief.exploration_mode = True
        brief.user_knowledge_level = "unknown"
        return brief

    def on_pipeline_clarify(
        self,
        *,
        result: PipelineResult,
        brief: AnalysisBrief,
        bridge: dict[str, Any] | None,
        analysis_id: str,
    ) -> tuple[AnalysisBrief, bool]:
        """Returns updated brief and whether pipeline should re-run immediately."""
        assert result.needs_clarification is not None
        if bridge and bridge.get("action") == "resolve_from_transcript":
            reply = ClarificationReply(analysis_id=analysis_id, answers=bridge.get("answers") or [])
            return apply_clarification_reply(brief, reply, result.needs_clarification), True
        return brief, False

    def suspend_response(
        self,
        *,
        session_id: str,
        analysis_id: str,
        request: ClarificationRequest,
        clarify_payload: dict[str, Any],
        workflow_status: str,
    ) -> ChatResponse:
        msg = request.evidence_summary or clarify_payload.get("user_message", "")
        return ChatResponse(
            session_id=session_id,
            analysis_id=analysis_id,
            workflow_status=workflow_status,
            outcome="needs_clarification",
            message=msg or clarify_payload.get("user_message", ""),
            clarification=request,
        )
