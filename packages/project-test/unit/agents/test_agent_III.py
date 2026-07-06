"""Agent III (risk-reviewer) one-way SQL gate."""

from __future__ import annotations

import json

import pytest

from project_core.domain.access.acl import build_permissions_snapshot
from risk_reviewer.service import RiskReviewerService

pytestmark = pytest.mark.unit

_PERMS = build_permissions_snapshot("user-1", "hq_analyst").model_dump(mode="json")


def _svc() -> RiskReviewerService:
    svc = object.__new__(RiskReviewerService)
    svc.skill = None
    svc.agent_key = "III"
    return svc


def _goal(payload: dict) -> str:
    return json.dumps({**payload, "permissions": _PERMS})


def test_III_approves_safe_select(decision_ctx):
    ctx = decision_ctx(
        goal=_goal(
            {
                "sql": "SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'",
                "allowed_tables": ["STRANS"],
            }
        )
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["verdict"] == "approve"


def test_III_rejects_drop(decision_ctx):
    ctx = decision_ctx(goal=_goal({"sql": "DROP TABLE STRANS", "allowed_tables": ["STRANS"]}))
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["verdict"] == "reject"
    assert payload["risk_feedback"] is not None


def test_III_accepts_explain_plan_and_risk_feedback_in_retry(decision_ctx, monkeypatch):
    monkeypatch.delenv("ALLOW_LLM_STUB", raising=False)
    captured: dict = {}

    class _FakeClient:
        def chat(self, **kwargs):
            captured["user"] = json.loads(kwargs["messages"][1]["content"])
            return type("R", (), {"content": json.dumps({"verdict": "approve", "concerns": []})})()

    monkeypatch.setattr("risk_reviewer.service.OpenRouterClient", lambda: _FakeClient())
    ctx = decision_ctx(
        goal=_goal(
            {
                "sql": "SELECT TOP 10 SKU_ID FROM STRANS",
                "allowed_tables": ["STRANS"],
                "explain_plan": {"estimated_rows": 1000},
                "risk_feedback": {"issue": "wide_scan"},
                "risk_attempt": 2,
            }
        )
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["verdict"] == "approve"
    assert captured["user"]["explain_plan"] == {"estimated_rows": 1000}
    assert captured["user"]["risk_feedback"] == {"issue": "wide_scan"}
    assert captured["user"]["risk_attempt"] == 2


def test_III_denied_without_permissions(decision_ctx):
    ctx = decision_ctx(goal=json.dumps({"sql": "SELECT 1", "allowed_tables": ["STRANS"]}))
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["verdict"] == "reject"
    assert "tool_not_granted:sql-gateway" in payload["concerns"]
