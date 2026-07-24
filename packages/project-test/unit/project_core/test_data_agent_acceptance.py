"""Data Agent CoT stub + acceptance trials for gift / 30325 / bill≥600k."""

from __future__ import annotations

from typing import Any

import pytest

from project_core.domain.analysis.data_agent_brain import run_data_agent_brain
from project_core.domain.analysis.ops import DatasetWorkingSet
from project_core.domain.contracts.brief import AnalysisBrief, TimeRange
from project_core.domain.contracts.sql_acl import SqlAclContext
from project_core.domain.data_fetch.recipes import GIFT_BILL_INTENT, gift_bill_threshold_chain
from project_core.domain.data_fetch.toolkit import DataFetchToolkit
from project_core.domain.feedback.analysis_tool_registry import AnalysisToolRegistry
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


class _ScriptedGw:
    """Returns scripted rows; records every SQL for assertions."""

    def __init__(self) -> None:
        self.sqls: list[str] = []

    def execute_readonly(self, sql: str, acl: SqlAclContext, *, target_db: str = "db2") -> dict[str, Any]:
        self.sqls.append(sql)
        u = sql.upper()
        if "FROM SKU_DEF" in u:
            rows = [{"SKU_ID": "ID30325", "SKU_CODE": "30325", "FULL_NAME": "Gift pad"}]
        elif "FROM TRANSHDR" in u:
            rows = [
                {
                    "TRANS_NUM": "B1",
                    "TRAN_DATE": "2026-07-03",
                    "TRAN_TIME": "12:00",
                    "STK_ID": 1,
                    "TRANS_CODE": "101",
                    "AMOUNT": 750000,
                },
                {
                    "TRANS_NUM": "B2",
                    "TRAN_DATE": "2026-07-04",
                    "TRAN_TIME": "13:00",
                    "STK_ID": 1,
                    "TRANS_CODE": "101",
                    "AMOUNT": 620000,
                },
            ]
        else:
            rows = [
                {
                    "TRANS_NUM": "B1",
                    "TRAN_DATE": "2026-07-03",
                    "TRAN_TIME": "11:00",
                    "STK_ID": 1,
                    "SKU_ID": "ID30325",
                    "TRANS_CODE": "221",
                    "QTY": 1,
                    "AMOUNT": 0,
                },
                {
                    "TRANS_NUM": "B2",
                    "TRAN_DATE": "2026-07-04",
                    "TRAN_TIME": "12:00",
                    "STK_ID": 1,
                    "SKU_ID": "ID30325",
                    "TRANS_CODE": "221",
                    "QTY": 1,
                    "AMOUNT": 0,
                },
            ]
        return {"rows": rows, "columns": list(rows[0].keys()), "row_count": len(rows)}


def _toolkit(fact_catalog: SchemaCatalog, tmp_path, gw: _ScriptedGw) -> DataFetchToolkit:
    policy = PolicyEngine(fact_catalog, allowed_tables=list(fact_catalog.tables()))
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    return DataFetchToolkit(
        sql_gateway=gw,
        policy=policy,
        acl=SqlAclContext(
            actor_id="trial",
            allowed_tables=list(fact_catalog.tables()),
            tool_grants=["tool:*"],
        ),
        working_set=ws,
        max_rows=5000,
    )


def test_stub_brain_resolve_first_no_trans_code_invent_header_grain(fact_catalog, tmp_path):
    gw = _ScriptedGw()
    toolkit = _toolkit(fact_catalog, tmp_path, gw)
    brief = AnalysisBrief(
        intent="gift 30325 bill >= 600k 1-6/7/2026",
        metrics=["qty", "bill_amount"],
        filters={"product_code": "30325", "min_bill_value": 600000},
        time_range=TimeRange(start="2026-07-01", end="2026-07-06"),
        output_format=["excel"],
    )
    payload = run_data_agent_brain(
        brief=brief,
        out_dir=str(tmp_path / "out"),
        fetch_toolkit=toolkit,
        working_set=toolkit.working_set,
        use_stub=True,
        max_planner_turns=12,
    )
    assert payload["action"] in {"complete", "partial"}
    assert payload["artifact_paths"], "expected excel artifact"
    obs = payload.get("observations") or []
    resolve_idx = next(i for i, o in enumerate(obs) if o.get("tool_id") == "resolve_products")
    lines_idx = next(
        i
        for i, o in enumerate(obs)
        if o.get("tool_id") == "query_rows" and o.get("save_as") in {"lines_probe", "sale_lines"}
    )
    bills_idx = next(
        i
        for i, o in enumerate(obs)
        if o.get("tool_id") == "query_rows" and o.get("save_as") == "bill_headers"
    )
    assert resolve_idx < lines_idx < bills_idx
    # No plan_sql / raw SQL in agent-visible observations
    for o in obs:
        assert "sql" not in o
        assert o.get("decision") != "plan_sql"
    # Gateway SQL must not invent TRANS_CODE equality filters
    for sql in gw.sqls:
        compact = sql.upper().replace(" ", "")
        assert "TRANS_CODE=" not in compact
        assert "TRANS_CODEIN(" not in compact
    # Bill grain via header AMOUNT
    hdr_sql = next(s for s in gw.sqls if "FROM TRANSHDR" in s.upper())
    assert "AMOUNT >=" in hdr_sql.upper()
    assert toolkit.working_set.has("bill_headers")
    assert float(toolkit.working_set.get("bill_headers").frame()["AMOUNT"].min()) >= 600000


def test_gift_recipe_chain_has_no_sql_and_stages(tmp_path):
    chain = gift_bill_threshold_chain(
        product_codes=["30325"],
        time_start="2026-07-01",
        time_end="2026-07-06",
        min_bill_value=600000,
    )
    assert chain[0]["tool_id"] == "resolve_products"
    assert chain[2]["tool_id"] == "query_rows"
    assert chain[2]["args"]["table"] == "TRANSHDR"
    assert chain[2]["args"]["min_amount"] == 600000
    blob = str(chain)
    assert "SELECT" not in blob.upper()
    assert "TRANS_CODE" not in blob

    class _Col:
        def __init__(self) -> None:
            self.docs: list[dict[str, Any]] = []

        def insert_one(self, doc: dict[str, Any]) -> None:
            self.docs.append(doc)

        def find(self, query: dict[str, Any]):
            return self

        def limit(self, n: int):
            return self.docs[:n]

    col = _Col()
    reg = AnalysisToolRegistry(col)
    rec = reg.stage_data_agent_chain(
        name="gift_30325",
        intent_pattern=GIFT_BILL_INTENT,
        steps=chain,
    )
    assert rec["kind"] == "data_agent_chain"
    assert not rec.get("sql_template")
    assert col.docs[0]["steps"][0]["tool_id"] == "resolve_products"


def test_data_agent_v2_flag_helper(monkeypatch):
    from types import SimpleNamespace

    from project_core.orchestration.pipeline import _data_agent_v2_enabled

    cfg = SimpleNamespace(pipeline=SimpleNamespace(data_agent_v2=False))
    monkeypatch.delenv("DATA_AGENT_V2", raising=False)
    assert _data_agent_v2_enabled(cfg) is False
    monkeypatch.setenv("DATA_AGENT_V2", "1")
    assert _data_agent_v2_enabled(cfg) is True
