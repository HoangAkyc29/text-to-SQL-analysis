"""Agent I (conversational-router) stub decide paths."""

from __future__ import annotations

import json

import pytest

from conversational_router.service import ConversationalRouterService

pytestmark = pytest.mark.unit


def _svc() -> ConversationalRouterService:
    return object.__new__(ConversationalRouterService)


def test_ingress_routes_analysis_for_vip(decision_ctx):
    ctx = decision_ctx(goal="Phân tích VIP doanh thu tháng 5")
    resp = _svc().decide(ctx)
    payload = json.loads(resp.content)
    assert payload["route"] == "analysis"
    assert payload["brief"] is not None


def test_ingress_chitchat(decision_ctx):
    ctx = decision_ctx(goal="Xin chào")
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["route"] == "chitchat"


def test_clarification_bridge_ask_user(decision_ctx):
    ctx = decision_ctx(
        metadata={
            "mode": "clarification_bridge",
            "clarification_request": {
                "reason": "missing",
                "partial_brief": {"intent": "VIP"},
                "questions": [
                    {"id": "vip_card_prefix", "prompt": "?", "options": [], "maps_to_brief_field": "filters.card_prefix"}
                ],
            },
            "transcript": [],
        }
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["action"] == "ask_user"


def test_clarify_mode_returns_mcq(decision_ctx):
    ctx = decision_ctx(
        metadata={
            "mode": "clarify",
            "clarification_request": {
                "reason": "r",
                "partial_brief": {"intent": "VIP"},
                "questions": [{"id": "q1", "prompt": "?", "options": [], "maps_to_brief_field": "filters.x"}],
            },
        }
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert "clarification" in payload
    assert payload["user_message"]


def test_synthesize_returns_outcome_message(decision_ctx):
    ctx = decision_ctx(metadata={"mode": "synthesize", "technical_summary": {"outcome": "success"}})
    payload = json.loads(_svc().decide(ctx).content)
    assert "success" in payload["user_message"]
