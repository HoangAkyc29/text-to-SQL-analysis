"""Case study link extraction tests."""

from __future__ import annotations

from project_core.domain.retrieval.link_extractor import extract_case_study_links
from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog
from project_core.paths import ROOT


def test_extract_links_from_gift_bill_sql():
    catalog = ColumnSemanticCatalog.from_columns_dir(ROOT / "data_dictionary" / "columns")
    sql = [
        "SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE LIKE '%30344%'",
        "SELECT s.SKU_ID, h.AMOUNT FROM STRANS s INNER JOIN TRANSHDR h ON s.TRANS_NUM = h.TRANS_NUM "
        "WHERE h.TRANS_CODE='113' AND h.AMOUNT >= 600000",
    ]
    links = extract_case_study_links(
        approved_sql=sql,
        schema_tables_used=["STRANS", "TRANSHDR", "SKU_DEF"],
        semantic_keys_used=["sku_id", "amount_bill_header"],
        column_catalog=catalog,
    )
    refs = {(l["chunk_group"], l["ref"]) for l in links}
    assert ("column", "sku_id") in refs or ("column", "sku_code") in refs
    assert ("table", "db2:strans") in refs or ("table", "strans") in refs


def test_extract_links_from_tool_chain():
    catalog = ColumnSemanticCatalog.from_columns_dir(ROOT / "data_dictionary" / "columns")
    chain = [
        {
            "kind": "fetch",
            "tool_id": "query_rows",
            "args": {
                "table": "TRANSHDR",
                "filters": [{"column": "AMOUNT", "op": "gte", "value": 600000}],
                "time_range": {"start": "2026-07-01", "end": "2026-07-06"},
            },
            "save_as": "bill_headers",
        }
    ]
    links = extract_case_study_links(tool_chain=chain, column_catalog=catalog)
    refs = {(l["chunk_group"], l["ref"]) for l in links}
    assert ("table", "db2:transhdr") in refs or ("table", "transhdr") in refs
