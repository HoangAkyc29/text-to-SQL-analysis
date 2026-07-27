"""Clarification bridge, resolver, enforcement."""

from __future__ import annotations

import pytest

from project_core.domain.clarification.bridge import ClarificationBridge
from project_core.domain.clarification.enforcement import can_emit_clarify, enforce_clarify_source
from project_core.domain.clarification.resolver import apply_clarification_reply
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import (
    ClarificationAnswer,
    ClarificationOption,
    ClarificationQuestion,
    ClarificationReply,
    ClarificationRequest,
)
from project_core.domain.memory.session_bundle import TranscriptTurn
from project_core.domain.workflow.state import new_workflow

pytestmark = pytest.mark.unit


def test_bridge_resolves_vip_from_transcript():
    request = ClarificationRequest(
        reason="missing",
        partial_brief=AnalysisBrief(intent="VIP points"),
        questions=[
            ClarificationQuestion(
                id="vip_card_prefix",
                prompt="VIP?",
                options=[],
                maps_to_brief_field="filters.card_prefix",
            )
        ],
    )
    transcript = [TranscriptTurn(id="1", role="user", content="VIP card prefix E trans_code 221", at="now")]
    result = ClarificationBridge().from_transcript_heuristic(request, transcript)
    assert result.action == "resolve_from_transcript"
    assert result.confidence >= 0.75


def test_bridge_ask_user_when_transcript_insufficient():
    request = ClarificationRequest(
        reason="missing",
        partial_brief=AnalysisBrief(intent="VIP"),
        questions=[
            ClarificationQuestion(
                id="vip_card_prefix",
                prompt="VIP?",
                options=[],
                maps_to_brief_field="filters.card_prefix",
            )
        ],
    )
    result = ClarificationBridge().from_transcript_heuristic(request, [])
    assert result.action == "ask_user"


def test_apply_clarification_reply_updates_brief():
    brief = AnalysisBrief(intent="VIP", filters={})
    request = ClarificationRequest(
        reason="r",
        partial_brief=brief,
        questions=[
            ClarificationQuestion(
                id="q1",
                prompt="p",
                options=[ClarificationOption(id="prefix_e", label="E", brief_value={"card_prefix": "E"})],
                maps_to_brief_field="filters.card_prefix",
            )
        ],
    )
    reply = ClarificationReply(
        analysis_id="a1",
        answers=[ClarificationAnswer(question_id="q1", selected_option_id="prefix_e")],
    )
    updated = apply_clarification_reply(brief, reply, request)
    assert updated.filters.get("card_prefix") == "E"
    requirement = updated.requirements[0]
    assert requirement.key == "card_prefix"
    assert requirement.source == "explicit"
    assert requirement.required is True


def test_enforce_clarify_source_II_only():
    req = ClarificationRequest(reason="r", partial_brief=AnalysisBrief(intent="x"), questions=[])
    enforce_clarify_source(req)


def test_can_emit_clarify_within_round_cap():
    wf = new_workflow("s", "u")
    wf.clarify_round = 2
    assert can_emit_clarify(wf) is True


def test_ensure_clarification_questions_synthesizes_amount_mcq():
    from project_core.domain.clarification.ensure import ensure_clarification_questions

    raw = ClarificationRequest(
        source_agent="IV",
        reason="missing AMOUNT after join — header amount or line amount (AMOUNT_x vs AMOUNT_y)?",
        partial_brief=AnalysisBrief(intent="gift bills"),
        questions=[],
    )
    fixed = ensure_clarification_questions(raw)
    assert len(fixed.questions) == 1
    assert fixed.questions[0].id == "bill_amount_grain"
    assert len(fixed.questions[0].options) >= 2


def test_ensure_clarification_questions_open_free_text():
    from project_core.domain.clarification.ensure import ensure_clarification_questions

    raw = ClarificationRequest(
        source_agent="IV",
        reason="Need store id for this report",
        partial_brief=AnalysisBrief(intent="x"),
        questions=[],
    )
    fixed = ensure_clarification_questions(raw)
    assert len(fixed.questions) == 1
    assert fixed.questions[0].options == []
    assert "store" in fixed.questions[0].prompt.lower() or "Need store" in fixed.questions[0].prompt
