"""Agent II (sql-planner) stub decide paths."""

from __future__ import annotations

import json

import pytest

from project_core.domain.access.acl import build_permissions_snapshot
from sql_planner.service import SqlPlannerService

pytestmark = pytest.mark.unit

_PERMS = build_permissions_snapshot("user-1", "hq_analyst").model_dump(mode="json")


def _svc() -> SqlPlannerService:
    return object.__new__(SqlPlannerService)


def _goal(payload: dict) -> str:
    return json.dumps({**payload, "permissions": _PERMS})


def test_II_clarify_when_vip_ambiguous(decision_ctx):
    ctx = decision_ctx(goal=_goal({"brief": {"intent": "VIP doanh thu"}, "inbox": {}, "attempt": 1}))
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["action"] == "clarify"
    assert payload["clarification_request"]["source_agent"] == "II"


def test_II_plan_sql_after_filter_set(decision_ctx):
    ctx = decision_ctx(
        goal=_goal({"brief": {"intent": "VIP", "filters": {"card_prefix": "E"}}, "inbox": {}, "attempt": 1})
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["action"] == "plan_sql"
    assert len(payload["sql_queries"]) >= 1


def test_II_reads_policy_feedback_in_inbox(decision_ctx):
    ctx = decision_ctx(
        goal=_goal(
            {
                "brief": {"intent": "VIP", "filters": {"card_prefix": "E"}},
                "inbox": {"policy_feedback": {"violations": ["table_not_allowed"]}},
                "attempt": 2,
            }
        )
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["action"] == "plan_sql"


def test_II_denied_without_permissions(decision_ctx):
    ctx = decision_ctx(goal=json.dumps({"brief": {"intent": "VIP"}, "inbox": {}, "attempt": 1}))
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["action"] == "impossible"
    assert payload["reason"] == "tool_not_granted:validate_sql"
