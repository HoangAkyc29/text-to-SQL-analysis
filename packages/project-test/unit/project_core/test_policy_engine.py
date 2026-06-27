from __future__ import annotations

from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.sql.policy_engine import PolicyEngine


def test_policy_allows_select():
    catalog = SchemaCatalog.from_dictionary_dir()
    engine = PolicyEngine(catalog, allowed_tables=catalog.tables())
    verdict = engine.validate("SELECT TOP 10 sale_id FROM sales")
    assert verdict.allowed is True
    assert verdict.sanitized_sql is not None


def test_policy_blocks_delete():
    catalog = SchemaCatalog.from_dictionary_dir()
    engine = PolicyEngine(catalog, allowed_tables=catalog.tables())
    verdict = engine.validate("DELETE FROM sales")
    assert verdict.allowed is False
