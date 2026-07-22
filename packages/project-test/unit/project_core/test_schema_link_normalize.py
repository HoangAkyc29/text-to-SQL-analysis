from __future__ import annotations

import pytest

from project_core.domain.feedback.schema_link_normalize import normalize_schema_links
from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog, ColumnSemanticMeta


pytestmark = pytest.mark.unit


def _catalog() -> ColumnSemanticCatalog:
    return ColumnSemanticCatalog(
        {
            "amount_bill_header": ColumnSemanticMeta(
                semantic_key="amount_bill_header",
                display_names=["AMOUNT"],
                tables=[{"ref": "db2:transhdr", "column": "AMOUNT"}],
            ),
            "amount_line_item": ColumnSemanticMeta(
                semantic_key="amount_line_item",
                display_names=["AMOUNT"],
                tables=[{"ref": "db2:strans", "column": "AMOUNT"}],
            ),
            "sale_document_number": ColumnSemanticMeta(
                semantic_key="sale_document_number",
                display_names=["TRANS_NUM"],
                tables=[
                    {"ref": "db2:transhdr", "column": "TRANS_NUM"},
                    {"ref": "db2:strans", "column": "TRANS_NUM"},
                ],
            ),
        }
    )


def test_normalize_canonical_passthrough() -> None:
    links = normalize_schema_links(
        [
            {"chunk_group": "table", "ref": "db2:transhdr"},
            {"chunk_group": "column", "ref": "amount_bill_header"},
        ],
        catalog=_catalog(),
    )
    assert {"chunk_group": "table", "ref": "db2:transhdr"} in links
    assert {"chunk_group": "column", "ref": "amount_bill_header"} in links


def test_normalize_bare_table_and_physical_column() -> None:
    links = normalize_schema_links(
        [
            {"table": "TRANSHDR"},
            {"table": "STRANS", "column": "AMOUNT"},
            {"table": "TRANSHDR", "column": "TRANS_NUM"},
        ],
        catalog=_catalog(),
    )
    refs = {(x["chunk_group"], x["ref"]) for x in links}
    assert ("table", "db2:transhdr") in refs
    assert ("table", "db2:strans") in refs
    assert ("column", "amount_line_item") in refs
    assert ("column", "sale_document_number") in refs


def test_normalize_dedupes() -> None:
    links = normalize_schema_links(
        [
            {"table": "STRANS"},
            {"chunk_group": "table", "ref": "db2:strans"},
            {"ref": "STRANS"},
        ],
        catalog=_catalog(),
    )
    tables = [x for x in links if x["chunk_group"] == "table"]
    assert len(tables) == 1
    assert tables[0]["ref"] == "db2:strans"
