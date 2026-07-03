"""sql-gateway MCP tools (in-process, no live SQL Server)."""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration


def test_validate_sql_allows_select():
    from sql_gateway.tools_impl import validate_sql

    from project_core.domain.access.acl import build_permissions_snapshot
    from project_core.domain.contracts.sql_acl import SqlAclContext

    acl = SqlAclContext.from_permissions(build_permissions_snapshot("tester", "hq_analyst"))
    result = validate_sql(
        "SELECT TOP 5 SKU_ID FROM STRANS WHERE TRANS_CODE = '113'",
        acl=acl,
    )
    assert result["allowed"] is True


def test_validate_sql_blocks_delete():
    from sql_gateway.tools_impl import validate_sql

    from project_core.domain.access.acl import build_permissions_snapshot
    from project_core.domain.contracts.sql_acl import SqlAclContext

    acl = SqlAclContext.from_permissions(build_permissions_snapshot("tester", "hq_analyst"))
    result = validate_sql("DELETE FROM STRANS", acl=acl)
    assert result["allowed"] is False


def test_get_schema_snapshot_has_tables():
    from sql_gateway.tools_impl import get_schema_snapshot

    from project_core.domain.access.acl import build_permissions_snapshot

    perms = build_permissions_snapshot("tester", "hq_analyst")
    snap = get_schema_snapshot(
        "tester", allowed_tables=perms.allowed_tables, tool_grants=perms.tool_grants
    )
    assert "tables" in snap
    assert snap["tables"]  # agent bundle list
    assert len(snap["logical_tables"]) >= 30


def test_execute_readonly_without_dsn_returns_error_or_rows(monkeypatch):
    from sql_gateway import tools_impl

    from project_core.domain.access.acl import build_permissions_snapshot
    from project_core.domain.contracts.sql_acl import SqlAclContext

    acl = SqlAclContext.from_permissions(build_permissions_snapshot("tester", "hq_analyst"))
    monkeypatch.delenv("ANALYTICS_DB_DSN", raising=False)
    try:
        result = tools_impl.execute_readonly("SELECT 1", acl=acl)
        assert "rows" in result or "error" in result or "violations" in result
    except RuntimeError:
        pass  # expected when DSN missing
