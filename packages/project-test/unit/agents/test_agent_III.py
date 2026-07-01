"""Agent III (risk-reviewer) one-way SQL gate."""

from __future__ import annotations

import json

import pytest

from risk_reviewer.service import RiskReviewerService

pytestmark = pytest.mark.unit


def _svc() -> RiskReviewerService:
    return object.__new__(RiskReviewerService)


def test_III_approves_safe_select(decision_ctx):
    ctx = decision_ctx(
        goal=json.dumps(
            {
                "sql": "SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'",
                "allowed_tables": ["STRANS"],
            }
        )
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["verdict"] == "approve"


def test_III_rejects_drop(decision_ctx):
    ctx = decision_ctx(goal=json.dumps({"sql": "DROP TABLE STRANS", "allowed_tables": ["STRANS"]}))
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["verdict"] == "reject"
    assert payload["risk_feedback"] is not None
