"""Agent I (conversational-router) stub decide paths."""

from __future__ import annotations

import json

import pytest

from conversational_router.service import (
    ConversationalRouterService,
    _normalize_requirement_provenance,
)

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


def test_requirement_provenance_keeps_inferred_metric_optional():
    brief = _normalize_requirement_provenance(
        "Show quantity by region",
        {
            "metrics": ["quantity", "revenue"],
            "dimensions": ["region"],
            "filters": {},
            "requirements": [
                {
                    "requirement_id": "metric:0",
                    "kind": "metric",
                    "key": "quantity",
                    "source": "explicit",
                    "required": True,
                    "evidence_quote": "quantity",
                    "value": "quantity",
                },
                {
                    "requirement_id": "metric:1",
                    "kind": "metric",
                    "key": "revenue",
                    "source": "explicit",
                    "required": True,
                    "evidence_quote": "revenue",
                    "value": "revenue",
                },
                {
                    "requirement_id": "dimension:0",
                    "kind": "dimension",
                    "key": "region",
                    "source": "explicit",
                    "required": True,
                    "evidence_quote": "by region",
                    "value": "region",
                },
            ],
        },
    )
    assert brief is not None
    requirements = {item["key"]: item for item in brief["requirements"]}
    assert requirements["quantity"]["required"] is True
    assert requirements["region"]["required"] is True
    assert requirements["revenue"]["source"] == "inferred"
    assert requirements["revenue"]["required"] is False


def test_requirement_provenance_recovers_explicit_time_and_ranking():
    brief = _normalize_requirement_provenance(
        "Show quantity from March 1 to March 3 and list 2 most recent rows by region",
        {
            "metrics": ["quantity"],
            "dimensions": ["region", "time"],
            "filters": {},
            "time_range": {
                "start": "2032-03-01",
                "end": "2032-03-03",
                "grain": "day",
            },
            "requirements": [
                {
                    "requirement_id": "metric:0",
                    "kind": "metric",
                    "key": "quantity",
                    "source": "explicit",
                    "required": True,
                    "evidence_quote": "quantity",
                },
                {
                    "requirement_id": "dimension:0",
                    "kind": "dimension",
                    "key": "region",
                    "source": "explicit",
                    "required": True,
                    "evidence_quote": "by region",
                },
                {
                    "requirement_id": "dimension:1",
                    "kind": "dimension",
                    "key": "time",
                    "source": "explicit",
                    "required": True,
                    "evidence_quote": "from March 1 to March 3",
                },
            ],
        },
    )
    assert brief is not None
    time_requirement = next(
        item for item in brief["requirements"] if item["kind"] == "time"
    )
    ranking_requirement = next(
        item for item in brief["requirements"] if item["kind"] == "ranking"
    )
    assert time_requirement["required"] is True
    assert ranking_requirement["value"]["limit"] == 2
    assert ranking_requirement["value"]["partition_by"] == "region"
