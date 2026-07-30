"""DataFetchToolkit flexible builders + policy wrap (no LLM SQL)."""

from __future__ import annotations

from typing import Any

import pytest

from project_core.domain.analysis.ops import DatasetWorkingSet
from project_core.domain.contracts.sql_acl import SqlAclContext
from project_core.domain.data_fetch import builders, flexible_builders as flex
from project_core.domain.data_fetch.toolkit import DataFetchToolkit
from project_core.domain.schema.catalog import ColumnMeta, SchemaCatalog, TableMeta
from project_core.domain.sql.policy_engine import PolicyEngine

pytestmark = pytest.mark.unit


@pytest.fixture
def fact_catalog() -> SchemaCatalog:
    def _tbl(name: str, cols: list[str]) -> TableMeta:
        return TableMeta(name=name, columns=[ColumnMeta(name=c, data_type="varchar") for c in cols])

    return SchemaCatalog(
        {
            "SKU_DEF": _tbl("SKU_DEF", ["SKU_ID", "SKU_CODE", "FULL_NAME"]),
            "STRANS": _tbl(
                "STRANS",
                ["TRANS_NUM", "TRAN_DATE", "TRAN_TIME", "STK_ID", "SKU_ID", "TRANS_CODE", "QTY", "AMOUNT"],
            ),
            "TRANSHDR": _tbl(
                "TRANSHDR",
                ["TRANS_NUM", "TRAN_DATE", "TRAN_TIME", "STK_ID", "TRANS_CODE", "AMOUNT"],
            ),
        }
    )


class _FakeGw:
    def __init__(self, rows_by_keyword: dict[str, list[dict[str, Any]]] | None = None) -> None:
        self.calls: list[dict[str, Any]] = []
        self.rows_by_keyword = rows_by_keyword or {}

    def execute_readonly(self, sql: str, acl: SqlAclContext, *, target_db: str = "db2") -> dict[str, Any]:
        self.calls.append({"sql": sql, "target_db": target_db, "acl": acl})
        upper = sql.upper()
        for key, rows in self.rows_by_keyword.items():
            if key.upper() in upper:
                cols = list(rows[0].keys()) if rows else []
                return {"rows": rows, "columns": cols, "row_count": len(rows)}
        return {"rows": [], "columns": [], "row_count": 0}


def test_query_rows_requires_time_on_facts():
    with pytest.raises(ValueError, match="pushdown_required|invalid_date"):
        flex.build_query_rows(table="STRANS", filters=[{"column": "SKU_ID", "op": "in", "value": ["1"]}], require_time=True)


def test_resolve_products_sql_is_exact_not_substring():
    sql = builders.build_resolve_products(codes=["30325"], hard_max=100)
    assert "LIKE '%' +" not in sql
    assert "LOWER(RTRIM(SKU_CODE)) = LOWER('30325')" in sql
    assert "PATINDEX" in sql


def test_resolve_products_name_contains_uses_full_name_u():
    sql = builders.build_resolve_products(name_contains="bánh chưng nương bắc", hard_max=100)
    assert "FULL_NAME_U" in sql
    assert "LIKE '%' + LOWER(N'bánh chưng nương bắc') + '%'" in sql
    assert "SKU_CODE" not in sql.split("WHERE", 1)[1] or "LOWER(RTRIM(SKU_CODE))" not in sql


def test_resolve_products_diverts_name_like_codes_to_full_name_u():
    sql = builders.build_resolve_products(codes=["bánh chưng nương bắc"], hard_max=100)
    assert "FULL_NAME_U" in sql
    assert "LIKE '%' +" in sql


def test_resolve_products_requires_codes_or_name():
    with pytest.raises(ValueError, match="codes_or_name_required"):
        builders.build_resolve_products(codes=[], hard_max=100)


def test_query_rows_sale_lines_parity():
    sql = flex.build_query_rows(
        table="STRANS",
        time_range={"start": "2026-07-01", "end": "2026-07-06"},
        filters=[{"column": "SKU_ID", "op": "in", "value": ["SKU1"]}],
        order_by=[{"column": "TRAN_DATE", "dir": "desc"}],
        require_time=True,
        hard_max=100,
    )
    assert "TRANS_CODE" not in sql.split("WHERE", 1)[1]
    assert "TRAN_DATE" in sql
    assert "SKU_ID IN" in sql


def test_query_rows_bill_headers_amount_threshold():
    sql = flex.build_query_rows(
        table="TRANSHDR",
        time_range={"start": "2026-07-01", "end": "2026-07-06"},
        filters=[{"column": "AMOUNT", "op": "gte", "value": 600000}],
        require_time=True,
        hard_max=100,
    )
    assert "AMOUNT >= 600000" in sql
    assert "FROM TRANSHDR" in sql


def test_preview_fact_without_time_rejected(fact_catalog, tmp_path):
    policy = PolicyEngine(fact_catalog, allowed_tables=list(fact_catalog.tables()))
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    toolkit = DataFetchToolkit(
        sql_gateway=_FakeGw(),
        policy=policy,
        acl=SqlAclContext(actor_id="t", allowed_tables=list(fact_catalog.tables()), tool_grants=["tool:*"]),
        working_set=ws,
        max_rows=100,
    )
    out = toolkit.execute("preview_table", {"table": "STRANS", "limit": 10})
    assert out["ok"] is False
    assert "pushdown_required" in out["error"]


def test_unsolicited_trans_code_rejected(fact_catalog, tmp_path):
    policy = PolicyEngine(fact_catalog, allowed_tables=list(fact_catalog.tables()))
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    toolkit = DataFetchToolkit(
        sql_gateway=_FakeGw(),
        policy=policy,
        acl=SqlAclContext(actor_id="t", allowed_tables=list(fact_catalog.tables()), tool_grants=["tool:*"]),
        working_set=ws,
        max_rows=100,
    )
    out = toolkit.execute(
        "query_rows",
        {
            "table": "STRANS",
            "sku_ids": ["X"],
            "time_range": {"start": "2026-07-01", "end": "2026-07-06"},
            "filters": [{"column": "TRANS_CODE", "op": "eq", "value": "113"}],
            "limit": 10,
        },
        brief={"filters": {"product_code": "30325"}},
    )
    assert out["ok"] is False
    assert out["error"] == "trans_code_filter_not_in_brief"


def test_deprecated_fetch_tool_rejected(fact_catalog, tmp_path):
    policy = PolicyEngine(fact_catalog, allowed_tables=list(fact_catalog.tables()))
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    toolkit = DataFetchToolkit(
        sql_gateway=_FakeGw(),
        policy=policy,
        acl=SqlAclContext(actor_id="t", allowed_tables=list(fact_catalog.tables()), tool_grants=["tool:*"]),
        working_set=ws,
        max_rows=100,
    )
    out = toolkit.execute("fetch_sale_lines", {"sku_ids": ["X"], "time_range": {"start": "2026-07-01", "end": "2026-07-06"}})
    assert out["ok"] is False
    assert "deprecated_fetch_tool" in out["error"]


def test_resolve_products_accepts_product_codes_alias(fact_catalog, tmp_path):
    gw = _FakeGw(
        {
            "SKU_DEF": [{"SKU_ID": "ID30325", "SKU_CODE": "30325", "FULL_NAME": "Gift"}],
        }
    )
    policy = PolicyEngine(fact_catalog, allowed_tables=list(fact_catalog.tables()))
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    toolkit = DataFetchToolkit(
        sql_gateway=gw,
        policy=policy,
        acl=SqlAclContext(actor_id="t", allowed_tables=list(fact_catalog.tables()), tool_grants=["tool:*"]),
        working_set=ws,
        max_rows=100,
    )
    out = toolkit.execute("resolve_products", {"product_codes": ["30325"]}, save_as="products")
    assert out["ok"] is True
    assert toolkit.fetch_attempts == 1
    assert toolkit.fetch_calls == 1
    assert any("product_codes->codes" in w for w in (out.get("warnings") or []))


def test_resolve_then_query_rows_omits_sql_from_payload(fact_catalog, tmp_path):
    gw = _FakeGw(
        {
            "SKU_DEF": [{"SKU_ID": "ID1", "SKU_CODE": "30325", "FULL_NAME": "Gift"}],
            "STRANS": [
                {
                    "TRANS_NUM": "T1",
                    "TRAN_DATE": "2026-07-01",
                    "TRAN_TIME": "10:00",
                    "STK_ID": 1,
                    "SKU_ID": "ID1",
                    "TRANS_CODE": "100",
                    "QTY": 1,
                    "AMOUNT": 10,
                }
            ],
        }
    )
    policy = PolicyEngine(fact_catalog, allowed_tables=list(fact_catalog.tables()))
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    toolkit = DataFetchToolkit(
        sql_gateway=gw,
        policy=policy,
        acl=SqlAclContext(actor_id="t", allowed_tables=list(fact_catalog.tables()), tool_grants=["tool:*"]),
        working_set=ws,
        max_rows=100,
    )
    r1 = toolkit.execute("resolve_products", {"codes": ["30325"]}, save_as="products")
    assert r1["ok"]
    assert "sql" not in r1
    r2 = toolkit.execute(
        "query_rows",
        {
            "table": "STRANS",
            "sku_ids": "products",
            "time_range": {"start": "2026-07-01", "end": "2026-07-06"},
            "limit": 10,
        },
        save_as="lines",
        brief={"filters": {"product_code": "30325"}},
    )
    assert r2["ok"] is True
    assert "sql" not in r2
    assert r2["row_count"] >= 1


def test_query_rows_master_table_omits_tran_date():
    sql = flex.build_query_rows(
        table="CUSTOMER",
        filters=[{"column": "CARD_ID", "op": "in", "value": ["A1"]}],
        time_range={"start": "2026-07-01", "end": "2026-07-06"},
        require_time=False,
    )
    assert "TRAN_DATE" not in sql
    assert "CARD_ID" in sql


def test_query_rows_fact_still_requires_tran_date():
    sql = flex.build_query_rows(
        table="STRANS",
        time_range={"start": "2026-07-01", "end": "2026-07-06"},
        require_time=True,
    )
    assert "TRAN_DATE >=" in sql


def test_auto_sku_ids_from_resolve(tmp_path, fact_catalog):
    import pandas as pd

    from project_core.domain.analysis.ops.working_set import DatasetHandle, DatasetWorkingSet
    from project_core.domain.contracts.sql_acl import SqlAclContext
    from project_core.domain.data_fetch.toolkit import DataFetchToolkit
    from project_core.domain.sql.policy_engine import PolicyEngine

    class _Gw:
        def __init__(self):
            self.sqls: list[str] = []
            self.last_sql = ""

        def execute_readonly(self, sql, acl, *, target_db="db2"):
            self.sqls.append(sql)
            self.last_sql = sql
            if "TRANS_NUM" in sql and "S1" not in sql:
                return {
                    "columns": ["TRANS_NUM", "SKU_ID", "CARD_ID"],
                    "rows": [
                        {"TRANS_NUM": "T1", "SKU_ID": "S1", "CARD_ID": "C1"},
                        {"TRANS_NUM": "T1", "SKU_ID": "S9", "CARD_ID": "C1"},
                    ],
                    "row_count": 2,
                }
            return {
                "columns": ["TRANS_NUM", "SKU_ID", "CARD_ID"],
                "rows": [{"TRANS_NUM": "T1", "SKU_ID": "S1", "CARD_ID": "C1"}],
                "row_count": 1,
            }

    gw = _Gw()
    policy = PolicyEngine(fact_catalog, allowed_tables=list(fact_catalog.tables()))
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    ws.put(
        DatasetHandle(
            ref="resolve_products",
            role="catalog",
            df=pd.DataFrame([{"SKU_ID": "S1", "SKU_CODE": "0001", "FULL_NAME_U": "x"}]),
        )
    )
    toolkit = DataFetchToolkit(
        sql_gateway=gw,
        policy=policy,
        acl=SqlAclContext(
            actor_id="t",
            allowed_tables=list(fact_catalog.tables()),
            tool_grants=["tool:*"],
        ),
        working_set=ws,
        max_rows=100,
    )
    out = toolkit.execute(
        "query_rows",
        {
            "table": "STRANS",
            "time_range": {"start": "2026-07-01", "end": "2026-07-06"},
            "limit": 50,
        },
        save_as="sale_lines",
        brief={"time_range": {"start": "2026-07-01", "end": "2026-07-06"}},
    )
    assert out["ok"] is True
    assert any("S1" in sql for sql in gw.sqls)
    assert any("auto_sku_ids_from_resolve" in w for w in (out.get("warnings") or []))
    assert not ws.has("sale_lines_all_bill_lines")


def test_trans_scope_drops_auto_sku(tmp_path, fact_catalog):
    import pandas as pd

    from project_core.domain.analysis.ops.working_set import DatasetHandle, DatasetWorkingSet
    from project_core.domain.contracts.sql_acl import SqlAclContext
    from project_core.domain.data_fetch.toolkit import DataFetchToolkit
    from project_core.domain.sql.policy_engine import PolicyEngine

    class _Gw:
        def __init__(self):
            self.last_sql = ""

        def execute_readonly(self, sql, acl, *, target_db="db2"):
            self.last_sql = sql
            return {
                "columns": ["TRANS_NUM", "SKU_ID"],
                "rows": [
                    {"TRANS_NUM": "T1", "SKU_ID": "S1"},
                    {"TRANS_NUM": "T1", "SKU_ID": "S9"},
                ],
                "row_count": 2,
            }

    gw = _Gw()
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    ws.put(
        DatasetHandle(
            ref="resolve_products",
            role="catalog",
            df=pd.DataFrame([{"SKU_ID": "S1", "SKU_CODE": "0001"}]),
        )
    )
    toolkit = DataFetchToolkit(
        sql_gateway=gw,
        policy=PolicyEngine(fact_catalog, allowed_tables=list(fact_catalog.tables())),
        acl=SqlAclContext(
            actor_id="t",
            allowed_tables=list(fact_catalog.tables()),
            tool_grants=["tool:*"],
        ),
        working_set=ws,
        max_rows=100,
    )
    out = toolkit.execute(
        "query_rows",
        {
            "table": "STRANS",
            "time_range": {"start": "2026-07-01", "end": "2026-07-06"},
            "trans_nums": ["T1"],
            "limit": 50,
        },
        brief={"time_range": {"start": "2026-07-01", "end": "2026-07-06"}},
    )
    assert out["ok"] is True
    assert "T1" in gw.last_sql
    assert "SKU_ID" not in gw.last_sql.upper()
    assert not any("auto_sku_ids_from_resolve" in w for w in (out.get("warnings") or []))


def test_auto_card_ids_from_bill_frames(tmp_path, fact_catalog):
    import pandas as pd

    from project_core.domain.analysis.ops.working_set import DatasetHandle, DatasetWorkingSet
    from project_core.domain.contracts.sql_acl import SqlAclContext
    from project_core.domain.data_fetch.toolkit import DataFetchToolkit
    from project_core.domain.sql.policy_engine import PolicyEngine

    class _Gw:
        def __init__(self):
            self.last_sql = ""

        def execute_readonly(self, sql, acl, *, target_db="db2"):
            self.last_sql = sql
            return {
                "columns": ["CARD_ID", "CUST_NAME", "PHONE"],
                "rows": [{"CARD_ID": "C1", "CUST_NAME": "A", "PHONE": "1"}],
                "row_count": 1,
            }

    gw = _Gw()
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    ws.put(
        DatasetHandle(
            ref="strans_lines",
            role="fact",
            df=pd.DataFrame([{"TRANS_NUM": "T1", "SKU_ID": "S1", "CARD_ID": "C1"}]),
        )
    )
    allowed = list(fact_catalog.tables()) + ["CUSTOMER", "CSCARD"]
    toolkit = DataFetchToolkit(
        sql_gateway=gw,
        policy=PolicyEngine(fact_catalog, allowed_tables=allowed),
        acl=SqlAclContext(actor_id="t", allowed_tables=allowed, tool_grants=["tool:*"]),
        working_set=ws,
        max_rows=100,
    )
    out = toolkit.execute("query_rows", {"table": "CUSTOMER", "limit": 50})
    assert out["ok"] is True
    assert "C1" in gw.last_sql
    assert any("auto_card_ids_from_bills" in w for w in (out.get("warnings") or []))


def test_auto_card_ids_prefers_product_scoped_frames(tmp_path, fact_catalog):
    import pandas as pd

    from project_core.domain.analysis.ops.working_set import DatasetHandle, DatasetWorkingSet
    from project_core.domain.contracts.sql_acl import SqlAclContext
    from project_core.domain.data_fetch.toolkit import DataFetchToolkit
    from project_core.domain.sql.policy_engine import PolicyEngine

    class _Gw:
        def __init__(self):
            self.last_sql = ""

        def execute_readonly(self, sql, acl, *, target_db="db2"):
            self.last_sql = sql
            return {
                "columns": ["CARD_ID", "CUST_NAME"],
                "rows": [{"CARD_ID": "C_PRODUCT", "CUST_NAME": "A"}],
                "row_count": 1,
            }

    gw = _Gw()
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    ws.put(
        DatasetHandle(
            ref="resolve_products",
            role="catalog",
            df=pd.DataFrame([{"SKU_ID": "S1", "SKU_CODE": "0001"}]),
        )
    )
    ws.put(
        DatasetHandle(
            ref="transhdr_data",
            role="fact",
            df=pd.DataFrame(
                [{"TRANS_NUM": f"H{i}", "CARD_ID": f"NOISE{i}"} for i in range(1200)]
            ),
        )
    )
    ws.put(
        DatasetHandle(
            ref="strans_lines",
            role="fact",
            df=pd.DataFrame([{"TRANS_NUM": "T1", "SKU_ID": "S1", "CARD_ID": "C_PRODUCT"}]),
        )
    )
    allowed = list(fact_catalog.tables()) + ["CUSTOMER", "CSCARD"]
    toolkit = DataFetchToolkit(
        sql_gateway=gw,
        policy=PolicyEngine(fact_catalog, allowed_tables=allowed),
        acl=SqlAclContext(actor_id="t", allowed_tables=allowed, tool_grants=["tool:*"]),
        working_set=ws,
        max_rows=100,
    )
    out = toolkit.execute("query_rows", {"table": "CUSTOMER", "limit": 50})
    assert out["ok"] is True
    assert "C_PRODUCT" in gw.last_sql
    assert "NOISE0" not in gw.last_sql


def test_rewrite_huge_trans_scope_to_product_bills(tmp_path, fact_catalog):
    import pandas as pd

    from project_core.domain.analysis.ops.working_set import DatasetHandle, DatasetWorkingSet
    from project_core.domain.contracts.sql_acl import SqlAclContext
    from project_core.domain.data_fetch.toolkit import DataFetchToolkit
    from project_core.domain.sql.policy_engine import PolicyEngine

    class _Gw:
        def __init__(self):
            self.last_sql = ""

        def execute_readonly(self, sql, acl, *, target_db="db2"):
            self.last_sql = sql
            return {
                "columns": ["TRANS_NUM", "SKU_ID"],
                "rows": [{"TRANS_NUM": "T1", "SKU_ID": "S9"}],
                "row_count": 1,
            }

    gw = _Gw()
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    ws.put(
        DatasetHandle(
            ref="resolve_products",
            role="catalog",
            df=pd.DataFrame([{"SKU_ID": "S1", "SKU_CODE": "0001"}]),
        )
    )
    ws.put(
        DatasetHandle(
            ref="strans_lines",
            role="fact",
            df=pd.DataFrame([{"TRANS_NUM": "T1", "SKU_ID": "S1", "CARD_ID": "C1"}]),
        )
    )
    huge = [f"H{i:04d}" for i in range(200)]
    toolkit = DataFetchToolkit(
        sql_gateway=gw,
        policy=PolicyEngine(fact_catalog, allowed_tables=list(fact_catalog.tables())),
        acl=SqlAclContext(
            actor_id="t",
            allowed_tables=list(fact_catalog.tables()),
            tool_grants=["tool:*"],
        ),
        working_set=ws,
        max_rows=5000,
    )
    out = toolkit.execute(
        "query_rows",
        {
            "table": "STRANS",
            "time_range": {"start": "2026-07-01", "end": "2026-07-06"},
            "filters": [{"column": "TRANS_NUM", "op": "in", "value": huge}],
            "limit": 5000,
        },
        brief={"time_range": {"start": "2026-07-01", "end": "2026-07-06"}},
    )
    assert out["ok"] is True
    assert "T1" in gw.last_sql
    assert "H0000" not in gw.last_sql
    assert any("rewrote_trans_scope_to_product_bills" in w for w in (out.get("warnings") or []))


def test_unexpanded_dataset_ref_fails_closed(tmp_path, fact_catalog):
    import pandas as pd

    from project_core.domain.analysis.ops.working_set import DatasetHandle, DatasetWorkingSet
    from project_core.domain.contracts.sql_acl import SqlAclContext
    from project_core.domain.data_fetch.toolkit import DataFetchToolkit
    from project_core.domain.sql.policy_engine import PolicyEngine

    class _Gw:
        def execute_readonly(self, sql, acl, *, target_db="db2"):
            return {"columns": ["CARD_ID"], "rows": [], "row_count": 0}

    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    ws.put(DatasetHandle(ref="unique_bills", role="fact", df=pd.DataFrame([{"CARD_ID": "   "}])))
    toolkit = DataFetchToolkit(
        sql_gateway=_Gw(),
        policy=PolicyEngine(
            fact_catalog,
            allowed_tables=list(fact_catalog.tables()) + ["CUSTOMER", "CSCARD"],
        ),
        acl=SqlAclContext(
            actor_id="t",
            allowed_tables=list(fact_catalog.tables()) + ["CUSTOMER", "CSCARD"],
            tool_grants=["tool:*"],
        ),
        working_set=ws,
        max_rows=100,
    )
    out = toolkit.execute(
        "query_rows",
        {
            "table": "CSCARD",
            "filters": [{"column": "CARD_ID", "op": "in", "value": "unique_bills.CARD_ID"}],
        },
    )
    assert out["ok"] is False
    assert "dataset_id_column_empty" in str(out.get("error") or "")
