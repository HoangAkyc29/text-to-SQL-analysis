"""Capability PermissionSet: wildcard matching, snapshot expansion, overrides."""

from __future__ import annotations

from project_core.domain.access.permission_set import (
    PermissionSet,
    capability_granted,
    tool_capability_for,
)


def test_capability_granted_exact_and_wildcard():
    grants = ["tool:sql-gateway:*", "function:*", "data:table:STRANS"]
    assert capability_granted(grants, "tool:sql-gateway:execute")
    assert capability_granted(grants, "function:any-id")
    assert capability_granted(grants, "data:table:STRANS")
    assert not capability_granted(grants, "tool:python-sandbox:plot_chart")
    assert not capability_granted(grants, "data:table:ACCOUNT")
    assert not capability_granted([], "tool:sql-gateway:execute")


def test_tool_capability_mapping():
    assert tool_capability_for("execute_readonly") == "tool:sql-gateway:execute"
    assert tool_capability_for("run_analysis_op") == "tool:analysis-ops:run_analysis_op"
    assert tool_capability_for("run_analysis_script") == "tool:python-sandbox:run_analysis_script"
    assert tool_capability_for("unknown_tool") == "tool:unknown_tool"


def test_full_access_snapshot_expands_all_tables():
    ps = PermissionSet.full_access()
    snap = ps.to_snapshot(
        actor_id="admin-1",
        role="admin",
        store_ids=None,
        all_tables=["STRANS", "PMTRANS", "ACCOUNT"],
    )
    assert sorted(snap.allowed_tables) == ["ACCOUNT", "PMTRANS", "STRANS"]
    assert snap.tool_grants == ["tool:*"]
    assert snap.allowed_functions == ["function:*"]
    assert snap.store_filter_required is False
    assert snap.denied_columns == []


def test_restricted_snapshot_from_keys():
    ps = PermissionSet.from_keys(
        [
            "data:table:STRANS",
            "data:table:PMTRANS",
            "data:column_deny:SPPRICE",
            "data:store_filter:required",
            "tool:sql-gateway:validate",
            "tool:sql-gateway:execute",
            "function:recipe-1",
        ]
    )
    snap = ps.to_snapshot(
        actor_id="mgr-1",
        role="store_manager",
        store_ids=[10001],
        all_tables=["STRANS", "PMTRANS", "ACCOUNT"],
    )
    assert sorted(snap.allowed_tables) == ["PMTRANS", "STRANS"]
    assert snap.denied_columns == ["SPPRICE"]
    assert snap.store_filter_required is True
    assert snap.store_ids == [10001]
    assert snap.tool_grants == ["tool:sql-gateway:execute", "tool:sql-gateway:validate"]
    assert snap.allowed_functions == ["function:recipe-1"]


def test_user_permission_revoke_override():
    # Simulate role grants minus a user-level revoke (as auth_store resolves).
    role_keys = {"tool:*", "function:*", "data:table:STRANS", "data:table:ACCOUNT"}
    role_keys.discard("data:table:ACCOUNT")  # revoke
    ps = PermissionSet.from_keys(role_keys)
    snap = ps.to_snapshot(
        actor_id="u",
        role="hq_analyst",
        store_ids=None,
        all_tables=["STRANS", "ACCOUNT"],
    )
    assert snap.allowed_tables == ["STRANS"]
    assert "ACCOUNT" not in snap.allowed_tables
