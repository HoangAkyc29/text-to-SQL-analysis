"""PolicyEngine edge cases."""

from __future__ import annotations

import pytest

from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.sql.policy_engine import PolicyEngine

pytestmark = pytest.mark.unit


@pytest.fixture
def engine(mini_schema_catalog):
    return PolicyEngine(mini_schema_catalog, allowed_tables=mini_schema_catalog.tables())


def test_policy_allows_select(engine):
    verdict = engine.validate("SELECT TOP 10 sale_id FROM sales")
    assert verdict.allowed is True
    assert verdict.sanitized_sql is not None


def test_policy_blocks_delete(engine):
    verdict = engine.validate("DELETE FROM sales")
    assert verdict.allowed is False


def test_policy_blocks_disallowed_table(engine):
    verdict = engine.validate("SELECT * FROM secret_table")
    assert verdict.allowed is False
    assert any("table_not_in_dictionary" in v for v in verdict.violations)


def test_policy_injects_row_limit(engine):
    verdict = engine.validate("SELECT sale_id FROM sales")
    assert verdict.allowed is True
    assert "LIMIT" in verdict.sanitized_sql.upper() or "TOP" in verdict.sanitized_sql.upper()


def test_policy_store_filter_when_required(mini_schema_catalog):
    engine = PolicyEngine(
        mini_schema_catalog,
        allowed_tables=mini_schema_catalog.tables(),
        store_ids=[1, 2],
        store_filter_required=True,
    )
    verdict = engine.validate("SELECT sale_id FROM sales")
    assert verdict.allowed is True
    assert "stk_id" in (verdict.sanitized_sql or "").lower()


def test_policy_rejects_logical_db_prefix(mini_schema_catalog):
    engine = PolicyEngine(mini_schema_catalog, allowed_tables=mini_schema_catalog.tables())
    verdict = engine.validate("SELECT TOP 5 sale_id FROM db2.dbo.sales")
    assert verdict.allowed is False
    assert "logical_db_prefix_forbidden" in verdict.violations


def test_policy_allows_cte_alias(mini_schema_catalog):
    engine = PolicyEngine(mini_schema_catalog, allowed_tables=mini_schema_catalog.tables())
    sql = (
        "WITH ranked AS (SELECT sale_id FROM sales) "
        "SELECT sale_id FROM ranked"
    )
    verdict = engine.validate(sql)
    assert verdict.allowed is True


def test_policy_blocks_semicolon_injection(engine):
    verdict = engine.validate("SELECT 1; DROP TABLE sales")
    assert verdict.allowed is False
