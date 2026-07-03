"""SQL gateway ACL enforcement — direct gateway calls must respect ACL."""

from __future__ import annotations

import pytest

from project_core.domain.access.acl import build_permissions_snapshot
from project_core.domain.contracts.sql_acl import SqlAclContext

pytestmark = pytest.mark.integration


def test_store_manager_blocked_on_forbidden_table():
    from sql_gateway.tools_impl import execute_readonly

    perms = build_permissions_snapshot("mgr-1", "store_manager", store_ids=[1])
    acl = SqlAclContext.from_permissions(perms)
    sql = "SELECT TOP 5 SPPRICE FROM HISRTPR"
    result = execute_readonly(sql, acl=acl)
    assert result.get("error") == "policy_blocked" or result.get("status") == "policy_blocked"
    assert result.get("violations")


def test_explain_sql_validates_before_plan():
    from sql_gateway.tools_impl import explain_sql

    perms = build_permissions_snapshot("mgr-1", "store_manager", store_ids=[1])
    acl = SqlAclContext.from_permissions(perms)
    result = explain_sql("SELECT SPPRICE FROM HISRTPR", acl=acl)
    assert result.get("status") == "policy_blocked"
    assert result.get("violations")


def test_hq_analyst_allowed_select():
    from sql_gateway.tools_impl import validate_sql

    perms = build_permissions_snapshot("hq-1", "hq_analyst")
    acl = SqlAclContext.from_permissions(perms)
    result = validate_sql(
        "SELECT TOP 5 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'",
        acl=acl,
    )
    assert result["allowed"] is True


def test_empty_allowed_tables_denied_by_default():
    from sql_gateway.tools_impl import execute_readonly, validate_sql

    acl = SqlAclContext(actor_id="anon", allowed_tables=[])
    sql = "SELECT TOP 5 SKU_ID FROM STRANS WHERE TRANS_CODE = '113'"
    assert validate_sql(sql, acl=acl)["allowed"] is False
    result = execute_readonly(sql, acl=acl)
    assert result.get("error") == "policy_blocked"
