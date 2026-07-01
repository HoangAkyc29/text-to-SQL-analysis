"""sql-gateway MCP tools (in-process, no live SQL Server)."""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration


def test_validate_sql_allows_select():
    from sql_gateway.tools_impl import validate_sql

    result = validate_sql("SELECT TOP 5 SKU_ID FROM STRANS WHERE TRANS_CODE = '113'", "tester")
    assert result["allowed"] is True


def test_validate_sql_blocks_delete():
    from sql_gateway.tools_impl import validate_sql

    result = validate_sql("DELETE FROM STRANS", "tester")
    assert result["allowed"] is False


def test_get_schema_snapshot_has_tables():
    from sql_gateway.tools_impl import get_schema_snapshot

    snap = get_schema_snapshot("tester")
    assert "tables" in snap
    assert snap["tables"]  # agent bundle list
    assert len(snap["logical_tables"]) >= 30


def test_execute_readonly_without_dsn_returns_error_or_rows(monkeypatch):
    from sql_gateway import tools_impl

    monkeypatch.delenv("ANALYTICS_DB_DSN", raising=False)
    try:
        result = tools_impl.execute_readonly("SELECT 1", "tester")
        assert "rows" in result or "error" in result or "violations" in result
    except RuntimeError:
        pass  # expected when DSN missing
