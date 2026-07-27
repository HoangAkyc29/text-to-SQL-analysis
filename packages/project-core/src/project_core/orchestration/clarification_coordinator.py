from __future__ import annotations

from typing import Any

from project_core.domain.clarification.bridge import ClarificationBridge
from project_core.domain.clarification.resolver import apply_clarification_reply
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import ClarificationReply, ClarificationRequest
from project_core.domain.contracts.feedback import DomainEvidence, DomainRuleCandidate
from project_core.domain.contracts.pipeline import ChatResponse, PipelineResult
from project_core.domain.memory.session_bundle import SessionBundle, TranscriptTurn
from project_core.domain.time import utc_now


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
            TranscriptTurn(
                id="resume",
                role="user",
                content=user_message,
                at=utc_now().isoformat(),
            ),
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

    def reusable_candidates_from_reply(
        self,
        *,
        request: ClarificationRequest,
        reply: ClarificationReply,
        actor_id: str,
        tenant_id: str = "",
        authority: str = "requester",
        trace_id: str,
    ) -> list[DomainRuleCandidate]:
        """Extract only clarification answers explicitly mapped as reusable facts.

        Ordinary brief mappings are ignored unless the question explicitly
        declares ``reusable_fact`` and concrete schema links. The legacy
        ``domain_facts.<table>.<column>`` marker remains accepted for old
        clarification payloads.
        """
        questions = {question.id: question for question in request.questions}
        candidates: list[DomainRuleCandidate] = []
        for answer in reply.answers:
            question = questions.get(answer.question_id)
            if question is None:
                continue
            parts = question.maps_to_brief_field.split(".")
            legacy_fact_mapping = len(parts) >= 3 and parts[0] == "domain_facts"
            if not question.reusable_fact and not legacy_fact_mapping:
                continue
            schema_links = list(question.schema_links)
            if legacy_fact_mapping and not schema_links:
                schema_links = [{"table": parts[1], "column": parts[2]}]
            if not schema_links:
                continue
            option = next(
                (item for item in question.options if item.id == answer.selected_option_id),
                None,
            )
            statement = (answer.other_text or (option.label if option else "")).strip()
            original_quote = (answer.evidence or statement).strip()
            if not statement or not original_quote:
                continue
            evidence = DomainEvidence(
                source_kind="clarification",
                source_ref=f"clarification:{answer.question_id}",
                quote=original_quote,
                actor_id=actor_id,
                trace_id=trace_id,
                schema_links=schema_links,
                confidence=1.0,
                independent_group=f"clarification:{actor_id}",
            )
            requested_scope = question.fact_scope
            scope = (
                "user"
                if authority == "requester"
                else requested_scope
                if authority == "admin"
                else "tenant"
            )
            candidates.append(
                DomainRuleCandidate(
                    fact_type=question.fact_type,
                    scope=scope,
                    actor_id=actor_id,
                    tenant_id=tenant_id,
                    statement=statement,
                    evidence_trace_ids=[trace_id],
                    evidence=[evidence],
                    schema_links=schema_links,
                    confidence=1.0,
                    authority=authority,  # type: ignore[arg-type]
                )
            )
        return candidates

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
        from project_core.domain.clarification.ensure import ensure_clarification_questions

        request = ensure_clarification_questions(request)
        msg = (
            str(clarify_payload.get("user_message") or "").strip()
            or request.evidence_summary
            or request.reason
            or "Cần thêm thông tin để tiếp tục phân tích."
        )
        return ChatResponse(
            session_id=session_id,
            analysis_id=analysis_id,
            workflow_status=workflow_status,
            outcome="needs_clarification",
            message=msg,
            clarification=request,
        )
