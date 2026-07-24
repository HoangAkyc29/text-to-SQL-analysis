"""Arg coerce: reject prose placeholders from Tool-Selector hints."""

from __future__ import annotations

import pytest

from project_core.domain.analysis.ops import DatasetWorkingSet
from project_core.domain.contracts.sql_acl import SqlAclContext
from project_core.domain.data_fetch.arg_coerce import (
    coerce_product_codes,
    coerce_table_name,
    coerce_time_range,
    looks_like_prose_placeholder,
    sanitize_filter_clauses,
)
from project_core.domain.data_fetch.toolkit import DataFetchToolkit
from project_core.domain.schema.catalog import ColumnMeta, SchemaCatalog, TableMeta
from project_core.domain.sql.policy_engine import PolicyEngine

pytestmark = pytest.mark.unit


def test_prose_time_range_falls_back_to_brief():
    prose = "brief_slice.time_range"
    assert looks_like_prose_placeholder(prose)
    out = coerce_time_range(prose, fallback={"start": "2026-07-01", "end": "2026-07-06"})
    assert out == {"start": "2026-07-01", "end": "2026-07-06"}


def test_dotted_brief_path_is_prose():
    assert looks_like_prose_placeholder("brief_slice.filters.min_bill_value")
    cleaned = sanitize_filter_clauses(
        [{"column": "BILL_AMT", "op": "gte", "value": "brief_slice.filters.min_bill_value"}]
    )
    assert cleaned == []


def test_dict_time_range_kept():
    out = coerce_time_range({"start": "2026-01-01", "end": "2026-01-31", "grain": "day"})
    assert out["start"] == "2026-01-01"
    assert out["grain"] == "day"


def test_sanitize_filters_drops_prose_and_normalizes_op():
    cleaned = sanitize_filter_clauses(
        [
            {"column": "AMOUNT", "operator": ">=", "value": 600000},
            {"column": "SKU_ID", "op": "in", "value": "SKU_ID from resolve_products dataset"},
            {"column": "STK_ID", "op": "eq", "value": "01"},
            "not-a-dict",
        ]
    )
    assert len(cleaned) == 2
    assert cleaned[0] == {"column": "AMOUNT", "op": "gte", "value": 600000}
    assert cleaned[1] == {"column": "STK_ID", "op": "eq", "value": "01"}


def test_coerce_table_and_codes():
    assert coerce_table_name("brief.table", fallback="STRANS") == "STRANS"
    assert coerce_table_name("TRANSHDR", fallback="STRANS") == "TRANSHDR"
    assert coerce_product_codes("codes from brief", fallback=["30325"]) == ["30325"]
    assert coerce_product_codes(["30325", "x from dataset"], fallback=[]) == ["30325"]


def test_toolkit_execute_survives_prose_time_range(tmp_path):
    catalog = SchemaCatalog(
        {
            "STRANS": TableMeta(
                name="STRANS",
                columns=[
                    ColumnMeta(name=c, data_type="varchar")
                    for c in ["TRANS_NUM", "TRAN_DATE", "TRAN_TIME", "STK_ID", "SKU_ID", "TRANS_CODE", "QTY", "AMOUNT"]
                ],
            )
        }
    )

    class _Gw:
        def execute_readonly(self, sql, acl, *, target_db="db2"):
            return {
                "rows": [{"TRANS_NUM": "1", "TRAN_DATE": "2026-07-02", "SKU_ID": "S1", "QTY": 1}],
                "columns": ["TRANS_NUM", "TRAN_DATE", "SKU_ID", "QTY"],
                "row_count": 1,
            }

    toolkit = DataFetchToolkit(
        sql_gateway=_Gw(),  # type: ignore[arg-type]
        policy=PolicyEngine(catalog, allowed_tables=["STRANS"]),
        acl=SqlAclContext(actor_id="t", allowed_tables=["STRANS"], tool_grants=["tool:*"], store_filter_required=False),
        working_set=DatasetWorkingSet(work_dir=tmp_path / "ws"),
        max_rows=100,
        max_fetch_calls=10,
    )
    result = toolkit.execute(
        "query_rows",
        {
            "table": "STRANS",
            "time_range": "brief_slice.time_range",
            "filters": [{"column": "SKU_ID", "op": "in", "value": "SKU_ID from resolve_products dataset"}],
            "limit": 10,
        },
        save_as="sale_lines",
        brief={"time_range": {"start": "2026-07-01", "end": "2026-07-06"}},
    )
    assert result.get("ok") is True, result
    assert "coerced_time_range_from_brief" in (result.get("warnings") or [])


def test_toolkit_drops_sku_ids_on_transhdr(tmp_path):
    catalog = SchemaCatalog(
        {
            "TRANSHDR": TableMeta(
                name="TRANSHDR",
                columns=[
                    ColumnMeta(name=c, data_type="varchar")
                    for c in ["TRANS_NUM", "TRAN_DATE", "TRAN_TIME", "STK_ID", "TRANS_CODE", "AMOUNT"]
                ],
            )
        }
    )

    class _Gw:
        def __init__(self) -> None:
            self.sqls: list[str] = []

        def execute_readonly(self, sql, acl, *, target_db="db2"):
            self.sqls.append(sql)
            return {
                "rows": [{"TRANS_NUM": "B1", "AMOUNT": 700000}],
                "columns": ["TRANS_NUM", "AMOUNT"],
                "row_count": 1,
            }

    gw = _Gw()
    toolkit = DataFetchToolkit(
        sql_gateway=gw,  # type: ignore[arg-type]
        policy=PolicyEngine(catalog, allowed_tables=["TRANSHDR"]),
        acl=SqlAclContext(actor_id="t", allowed_tables=["TRANSHDR"], tool_grants=["tool:*"], store_filter_required=False),
        working_set=DatasetWorkingSet(work_dir=tmp_path / "ws"),
        max_rows=100,
    )
    result = toolkit.execute(
        "query_rows",
        {
            "table": "TRANSHDR",
            "time_range": {"start": "2026-07-01", "end": "2026-07-06"},
            "sku_ids": ["SKU1"],
            "min_amount": 600000,
            "limit": 10,
        },
        save_as="bill_headers",
        brief={"time_range": {"start": "2026-07-01", "end": "2026-07-06"}},
    )
    assert result.get("ok") is True, result
    assert "dropped_sku_ids_on_header_table" in (result.get("warnings") or [])
    assert "SKU_ID" not in gw.sqls[0].upper()
    assert "AMOUNT" in gw.sqls[0].upper()


def test_toolkit_resolves_dataset_dot_column(tmp_path):
    import pandas as pd

    catalog = SchemaCatalog(
        {
            "STRANS": TableMeta(
                name="STRANS",
                columns=[
                    ColumnMeta(name=c, data_type="varchar")
                    for c in ["TRANS_NUM", "TRAN_DATE", "TRAN_TIME", "STK_ID", "SKU_ID", "TRANS_CODE", "QTY", "AMOUNT"]
                ],
            )
        }
    )
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    ws.save_frame("resolve_products", pd.DataFrame([{"SKU_ID": "SKU99", "SKU_CODE": "30325"}]), role="fetch")

    class _Gw:
        def __init__(self) -> None:
            self.sqls: list[str] = []

        def execute_readonly(self, sql, acl, *, target_db="db2"):
            self.sqls.append(sql)
            return {"rows": [{"SKU_ID": "SKU99"}], "columns": ["SKU_ID"], "row_count": 1}

    gw = _Gw()
    toolkit = DataFetchToolkit(
        sql_gateway=gw,  # type: ignore[arg-type]
        policy=PolicyEngine(catalog, allowed_tables=["STRANS"]),
        acl=SqlAclContext(actor_id="t", allowed_tables=["STRANS"], tool_grants=["tool:*"], store_filter_required=False),
        working_set=ws,
        max_rows=100,
    )
    result = toolkit.execute(
        "query_rows",
        {
            "table": "STRANS",
            "time_range": {"start": "2026-07-01", "end": "2026-07-06"},
            "filters": [{"column": "SKU_ID", "op": "in", "value": "resolve_products.SKU_ID"}],
            "limit": 10,
        },
        save_as="sale_lines",
    )
    assert result.get("ok") is True, result
    assert "SKU99" in gw.sqls[0]
    assert "resolve_products.SKU_ID" not in gw.sqls[0]
