"""Policy + data_dictionary integration."""

from __future__ import annotations

import pytest

from project_core.domain.access.acl import build_permissions_snapshot
from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.sql.policy_engine import PolicyEngine

pytestmark = pytest.mark.unit


@pytest.fixture
def catalog():
    return SchemaCatalog.from_dictionary_dir()


def test_sql_table_names_include_shards(catalog):
    names = catalog.sql_table_names()
    assert "strans" in names
    assert "strans_202504" in names
    assert "pmtrans" in names


def test_policy_blocks_non_dictionary_table(catalog):
    engine = PolicyEngine(catalog, allowed_tables=build_permissions_snapshot("u", "hq_analyst").allowed_tables)
    verdict = engine.validate("SELECT TOP 10 * FROM secret_table")
    assert not verdict.allowed
    assert any("table_not_in_dictionary" in v for v in verdict.violations)


def test_policy_allows_dictionary_table(catalog):
    perms = build_permissions_snapshot("u", "hq_analyst")
    engine = PolicyEngine(catalog, allowed_tables=perms.allowed_tables)
    verdict = engine.validate("SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'")
    assert verdict.allowed


def test_policy_blocks_delete(catalog):
    engine = PolicyEngine(catalog, allowed_tables=["STRANS"])
    verdict = engine.validate("DELETE FROM STRANS")
    assert not verdict.allowed
    assert "select_only" in verdict.violations


def test_store_manager_cannot_query_hissppr(catalog):
    perms = build_permissions_snapshot("u", "store_manager")
    engine = PolicyEngine(catalog, allowed_tables=perms.allowed_tables)
    verdict = engine.validate("SELECT TOP 10 SPPRICE FROM HISSPPR")
    assert not verdict.allowed
    assert any("table_not_allowed" in v for v in verdict.violations)


def test_agent_schema_bundle_has_descriptions(catalog):
    perms = build_permissions_snapshot("u", "hq_analyst")
    bundle = catalog.agent_schema_bundle(perms.allowed_tables)
    assert bundle["tables"]
    assert any(t.get("description") for t in bundle["tables"])
    assert bundle["domain_definitions_excerpt"]
