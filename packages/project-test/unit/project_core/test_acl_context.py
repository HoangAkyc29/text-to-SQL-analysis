"""ACL and context policy."""

from __future__ import annotations

import pytest

from project_core.domain.access.acl import build_permissions_snapshot, can_access_table
from project_core.domain.access.context_policy import ContextPolicy
from project_core.domain.memory.session_bundle import SessionBundle

pytestmark = pytest.mark.unit


def test_store_manager_requires_store_filter():
    snap = build_permissions_snapshot("u", "store_manager", store_ids=[1])
    assert snap.store_filter_required is True
    assert snap.store_ids == [1]


def test_hq_analyst_has_broader_tables():
    snap = build_permissions_snapshot("u", "hq_analyst")
    assert "promotions" in snap.allowed_tables or len(snap.allowed_tables) >= 6


def test_context_policy_agent_II_gets_brief():
    policy = ContextPolicy()
    session = SessionBundle(session_id="s", actor_id="u")
    ctx = policy.build_request_context("II", "u", session, extra={"inbox": {"policy_feedback": {}}})
    assert ctx["agent"] == "II"
    assert "inbox" in str(ctx) or "workflow_steps" in ctx


def test_context_policy_IV_sandbox_tools_only():
    policy = ContextPolicy()
    tools = policy.allowed_mcp_tools("IV")
    assert "run_analysis_script" in tools
    assert not any("execute_readonly" in t for t in tools)
