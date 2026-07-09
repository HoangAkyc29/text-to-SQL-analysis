"""Column semantic catalog tests."""

from __future__ import annotations

from pathlib import Path

from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog
from project_core.paths import ROOT


def test_column_catalog_loads_sale_document_number():
    catalog = ColumnSemanticCatalog.from_columns_dir(ROOT / "data_dictionary" / "columns")
    assert len(catalog.semantic_keys()) > 50
    trans = catalog.get("sale_document_number")
    assert trans is not None
    assert "TRANS_NUM" in trans.display_names
    assert len(trans.tables) >= 2


def test_semantic_for_column_lookup():
    catalog = ColumnSemanticCatalog.from_columns_dir(ROOT / "data_dictionary" / "columns")
    meta = catalog.semantic_for_column("db2:transhdr", "AMOUNT")
    assert meta is not None
    assert meta.semantic_key == "amount_bill_header"


def test_embed_text_includes_facts():
    catalog = ColumnSemanticCatalog.from_columns_dir(ROOT / "data_dictionary" / "columns")
    text = catalog.embed_text("sale_line_document_type")
    assert "113" in text or "bán" in text.lower() or "trans_code" in text.lower()
