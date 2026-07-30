"""Guards: no name-type guesses; top-N + SKU evidence on deliverables."""

from __future__ import annotations

import pandas as pd
import pytest

from project_core.domain.analysis import data_agent_brain as brain
from project_core.domain.analysis.data_agent_guards import (
    assess_deliverable_coverage,
    coverage_forces_partial,
    infer_top_n,
    is_blocked_name_type_guess,
    is_blocked_premature_export,
    is_nonblocking_type_clarify,
    needs_bill_deliverable,
    needs_customer_profile,
    prefer_export_dataset_ref,
    ranking_targets_bills,
)
from project_core.domain.analysis.ops import DatasetWorkingSet, execute_op
from project_core.domain.contracts.brief import AnalysisBrief, BriefRequirement, TimeRange
from project_core.domain.contracts.sql_acl import SqlAclContext
from project_core.domain.data_fetch.toolkit import DataFetchToolkit
from project_core.domain.schema.catalog import ColumnMeta, SchemaCatalog, TableMeta
from project_core.domain.sql.policy_engine import PolicyEngine

pytestmark = pytest.mark.unit


def test_infer_top_n_from_intent_and_filters():
    brief = AnalysisBrief(
        intent="lay 5 bill gan nhat cho ma 30325",
        filters={"product_code": "30325"},
    )
    assert infer_top_n(brief) == 5
    brief2 = AnalysisBrief(
        intent="report",
        filters={"product_code": "30325", "top_n": 3},
    )
    assert infer_top_n(brief2) == 3
    brief3 = AnalysisBrief(
        intent="x",
        requirements=[
            BriefRequirement(
                requirement_id="ranking:top_bills",
                kind="ranking",
                key="top_5_bills",
                value={"n": 5},
            )
        ],
    )
    assert infer_top_n(brief3) == 5


def test_ranking_targets_bills_vs_products():
    product_brief = AnalysisBrief(
        intent="top 10 mặt hàng doanh thu cao nhất từ 22/7",
        metrics=["revenue", "quantity"],
    )
    bill_brief = AnalysisBrief(intent="lay 5 bill gan nhat cho ma 30325")
    assert ranking_targets_bills(product_brief) is False
    assert ranking_targets_bills(bill_brief) is True
    assert needs_bill_deliverable(product_brief) is False
    assert needs_bill_deliverable(bill_brief) is True


def test_needs_customer_profile_without_deliverables_field():
    brief = AnalysisBrief(intent="top 10 mặt hàng doanh thu")
    assert needs_customer_profile(brief) is False
    assert needs_bill_deliverable(brief) is False


def test_prefer_export_aggregate_over_raw_bill_lines():
    """Product-ranking briefs must export the ranked frame, not raw STRANS probes."""
    ws = DatasetWorkingSet()
    ws.save_frame(
        "strans_lines",
        pd.DataFrame(
            {
                "TRANS_NUM": [f"B{i}" for i in range(100)],
                "SKU_ID": [f"S{i % 10}" for i in range(100)],
                "AMOUNT": [1.0] * 100,
            }
        ),
        source="fetch",
        role="fact",
    )
    ws.save_frame(
        "top_10_skus_by_revenue",
        pd.DataFrame(
            {
                "SKU_ID": [f"S{i}" for i in range(10)],
                "total_revenue": [100 - i for i in range(10)],
                "total_quantity": [10 - i for i in range(10)],
            }
        ),
        source="top_n_per_group",
        role="aggregate",
    )
    chosen = prefer_export_dataset_ref(ws, needs_bill=False)
    assert chosen == "top_10_skus_by_revenue"


def test_block_catalog_export_when_bill_checklist():
    ws = DatasetWorkingSet()
    ws.save_frame(
        "resolved_skus",
        pd.DataFrame(
            {"SKU_ID": ["1"], "SKU_CODE": ["30344"], "FULL_NAME": ["X"]}
        ),
        source="resolve_products",
        role="catalog",
    )
    ws.save_frame(
        "sale_lines",
        pd.DataFrame(
            {
                "TRANS_NUM": ["B1"],
                "SKU_ID": ["1"],
                "QTY": [1],
            }
        ),
        source="fetch",
        role="fact",
    )
    assert (
        is_blocked_premature_export(
            checklist={"top_n": 5, "min_bill_value": 600000},
            dataset="resolved_skus",
            working_set=ws,
        )
        == "blocked_export_product_catalog_before_bills"
    )
    assert (
        is_blocked_premature_export(
            checklist={"top_n": 5},
            dataset="sale_lines",
            working_set=ws,
        )
        is None
    )
    ws.save_frame(
        "joined_sales_data",
        pd.DataFrame(
            {
                "TRANS_NUM": ["B1", "B2"],
                "SKU_ID": ["1", "1"],
                "QTY": [1, 1],
                "TRAN_DATE": ["2026-07-01", "2026-07-02"],
            }
        ),
        source="join",
        role="fact",
    )
    ws.save_frame(
        "total_quantity_sold_per_product",
        pd.DataFrame({"SKU_ID": ["1"], "QTY_sum": [2]}),
        source="groupby_agg",
        role="aggregate",
    )
    assert (
        is_blocked_premature_export(
            checklist={"top_n": 5, "min_bill_value": 600000},
            dataset="total_quantity_sold_per_product",
            working_set=ws,
        )
        is not None
    )
    assert prefer_export_dataset_ref(ws, needs_bill=True) in {
        "joined_sales_data",
        "sale_lines",
    }


def test_prefer_export_skips_empty_bill_frames():
    ws = DatasetWorkingSet()
    ws.save_frame(
        "filtered_sale_lines",
        pd.DataFrame(
            columns=["TRANS_NUM", "SKU_ID", "QTY", "TRAN_DATE"]
        ),
        source="filter",
        role="fact",
    )
    ws.save_frame(
        "joined_sales_data",
        pd.DataFrame(
            {
                "TRANS_NUM": ["B1", "B2"],
                "SKU_ID": ["1", "1"],
                "QTY": [1, 1],
                "TRAN_DATE": ["2026-07-01", "2026-07-02"],
            }
        ),
        source="join",
        role="fact",
    )
    assert prefer_export_dataset_ref(ws, needs_bill=True) == "joined_sales_data"


def test_prefer_export_prefers_partitioned_top_n_over_join():
    ws = DatasetWorkingSet()
    ws.save_frame(
        "joined_sales_data",
        pd.DataFrame(
            {
                "TRANS_NUM": [f"B{i}" for i in range(20)],
                "SKU_ID": ["1"] * 10 + ["2"] * 10,
                "QTY": [1] * 20,
                "TRAN_DATE": ["2026-07-01"] * 20,
            }
        ),
        source="join",
        role="fact",
    )
    ws.save_frame(
        "top_5_bills_per_product",
        pd.DataFrame(
            {
                "TRANS_NUM": [f"B{i}" for i in range(10)],
                "SKU_ID": ["1"] * 5 + ["2"] * 5,
                "QTY": [1] * 10,
                "TRAN_DATE": ["2026-07-02"] * 10,
            }
        ),
        source="top_n_per_group",
        role="fact",
        op_id="top_n_per_group",
    )
    assert prefer_export_dataset_ref(ws, needs_bill=True) == "top_5_bills_per_product"


def test_prefer_export_skips_catalog_when_bill_frames_exist_even_without_top_n():
    ws = DatasetWorkingSet()
    ws.save_frame(
        "resolve_products",
        pd.DataFrame(
            {"SKU_ID": ["290003050900"], "SKU_CODE": ["00030509"], "FULL_NAME_U": ["x"]}
        ),
        source="resolve_products",
        role="catalog",
    )
    ws.save_frame(
        "strans_lines",
        pd.DataFrame(
            {
                "TRANS_NUM": ["B1", "B2"],
                "SKU_ID": ["290003050900", "290003050900"],
                "CARD_ID": ["C1", "C2"],
                "QTY": [1, 2],
            }
        ),
        source="query_rows",
        role="fact",
    )
    chosen = prefer_export_dataset_ref(
        ws, needs_bill=False, product_codes=["00030509"]
    )
    assert chosen == "strans_lines"
    assert (
        is_blocked_premature_export(
            checklist={},
            dataset="resolve_products",
            working_set=ws,
        )
        == "blocked_export_product_catalog_before_bills"
    )


def test_rank_bill_frame_keeps_partitioned_top_n(tmp_path):
    from project_core.domain.analysis.data_agent_guards import rank_bill_frame_for_export

    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    out = tmp_path / "out"
    out.mkdir()
    ws.save_frame(
        "top_5_bills_per_product",
        pd.DataFrame(
            {
                "TRANS_NUM": [f"B{i}" for i in range(15)],
                "SKU_ID": ["A"] * 5 + ["B"] * 5 + ["C"] * 5,
                "TRAN_DATE": ["2026-07-01"] * 15,
            }
        ),
        source="top_n_per_group",
        role="fact",
        op_id="top_n_per_group",
    )
    ref = rank_bill_frame_for_export(
        ws,
        source_ref="top_5_bills_per_product",
        top_n=5,
        out_dir=out,
        save_as="bills_top_n",
    )
    assert ref == "bills_top_n"
    assert len(ws.get("bills_top_n").frame()) == 15


def test_coverage_allows_per_group_top_n_row_count():
    from project_core.domain.analysis.data_agent_guards import assess_deliverable_coverage

    ws = DatasetWorkingSet()
    ws.save_frame(
        "top_5_bills_per_product",
        pd.DataFrame(
            {
                "TRANS_NUM": [f"B{i}" for i in range(15)],
                "SKU_ID": ["A"] * 5 + ["B"] * 5 + ["C"] * 5,
                "TRAN_DATE": ["2026-07-01"] * 15,
                "QTY": [1] * 15,
            }
        ),
        source="top_n_per_group",
        role="fact",
        op_id="top_n_per_group",
    )
    brief = AnalysisBrief(
        intent="5 bill moi ma",
        filters={"product_code": ["A", "B", "C"], "top_n": 5},
    )
    cov = assess_deliverable_coverage(
        brief, ws, product_codes=["A", "B", "C"], top_n=5
    )
    assert cov["ok"], cov
    assert not any(str(g).startswith("top_n_mismatch") for g in cov["gaps"])


def test_coverage_rejects_catalog_excel_when_top_n_bills(tmp_path):
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    ws.set_output_root(tmp_path / "out")
    ws.save_frame(
        "resolved_skus",
        pd.DataFrame(
            {"SKU_ID": ["1"], "SKU_CODE": ["30344"], "FULL_NAME": ["X"]}
        ),
        role="catalog",
    )
    execute_op(
        ws,
        "export_excel",
        {"dataset": "resolved_skus", "filename": "analysis_result.xlsx"},
        out_dir=tmp_path / "out",
    )
    brief = AnalysisBrief(
        intent="lay 5 bill",
        filters={"product_code": ["30344"], "top_n": 5, "min_bill_value": 600000},
    )
    cov = assess_deliverable_coverage(brief, ws, product_codes=["30344"], top_n=5)
    assert not cov["ok"]
    assert "missing_bill_evidence_columns" in cov["gaps"] or "catalog_export_without_bills" in cov["gaps"]
    assert coverage_forces_partial(cov["gaps"])


def test_block_display_name_filters_when_codes_present():
    codes = ["30344", "30348"]
    assert (
        is_blocked_name_type_guess(
            product_codes=codes,
            op_id="filter_rows",
            args={
                "dataset": "joined",
                "conditions": [{"column": "FULL_NAME", "operator": "contains", "value": "ANY"}],
            },
        )
        == "blocked_name_type_guess"
    )
    assert (
        is_blocked_name_type_guess(
            product_codes=codes,
            op_id="filter_rows",
            args={
                "dataset": "joined",
                "column": "FULL_NAME",
                "op": "contains",
                "value": "x",
            },
        )
        == "blocked_name_type_guess"
    )
    assert (
        is_blocked_name_type_guess(
            product_codes=[],
            op_id="filter_rows",
            args={
                "dataset": "joined",
                "conditions": [{"column": "FULL_NAME", "op": "contains", "value": "ANY"}],
            },
        )
        is None
    )
    assert (
        is_blocked_name_type_guess(
            product_codes=codes,
            op_id="filter_rows",
            args={
                "dataset": "joined",
                "conditions": [{"column": "AMOUNT", "op": "gte", "value": 600000}],
            },
        )
        is None
    )


def test_deliverable_coverage_top_n_and_sku_columns(tmp_path):
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    out = tmp_path / "out"
    out.mkdir()
    df = pd.DataFrame(
        {
            "TRANS_NUM": [f"B{i}" for i in range(10)],
            "bill_value": [700000] * 10,
            "quantity": [1] * 10,
        }
    )
    ws.save_frame("final", df, role="analysis")
    execute_op(
        ws,
        "export_excel",
        {"dataset": "final", "filename": "analysis_result.xlsx"},
        out_dir=out,
    )
    brief = AnalysisBrief(
        intent="5 bill gan nhat",
        filters={"product_code": ["30344", "30348"], "top_n": 5},
        metrics=["quantity"],
    )
    cov = assess_deliverable_coverage(brief, ws, product_codes=["30344", "30348"], top_n=5)
    assert cov["ok"] is False
    assert any(g.startswith("top_n_mismatch") for g in cov["gaps"])
    # Quantity + product_codes must NOT invent a SKU-column evidence gap.
    assert "missing_sku_evidence_columns" not in cov["gaps"]
    assert coverage_forces_partial(cov["gaps"]) is True

    df2 = pd.DataFrame(
        {
            "TRANS_NUM": ["B1", "B2", "B3", "B4"],
            "SKU_CODE": ["30344"] * 4,
            "bill_value": [700000] * 4,
        }
    )
    ws2 = DatasetWorkingSet(work_dir=tmp_path / "ws2")
    out2 = tmp_path / "out2"
    out2.mkdir()
    ws2.save_frame("final", df2, role="analysis")
    execute_op(
        ws2,
        "export_excel",
        {"dataset": "final", "filename": "analysis_result.xlsx"},
        out_dir=out2,
    )
    cov2 = assess_deliverable_coverage(brief, ws2, product_codes=["30344"], top_n=5)
    assert "missing_sku_evidence_columns" not in cov2["gaps"]
    assert not any(g.startswith("top_n_mismatch") for g in cov2["gaps"])
    assert any(c.startswith("fewer_than_requested") for c in cov2["caveats"])
    assert cov2["ok"] is True


def test_coverage_allows_bill_export_without_sku_when_quantity_metric(tmp_path):
    """UI-style case: joined bills without SKU cols + quantity metric → no sku gap."""
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    out = tmp_path / "out"
    out.mkdir()
    df = pd.DataFrame(
        {
            "TRANS_NUM": ["B1", "B2", "B3", "B4"],
            "AMOUNT": [700000] * 4,
            "QTY": [1, 2, 1, 1],
        }
    )
    ws.save_frame("joined", df, role="analysis")
    execute_op(
        ws,
        "export_excel",
        {"dataset": "joined", "filename": "analysis_result.xlsx"},
        out_dir=out,
    )
    brief = AnalysisBrief(
        intent="5 bill",
        filters={"product_code": "30325", "top_n": 5, "min_bill_value": 600000},
        metrics=["quantity", "bill_value"],
    )
    cov = assess_deliverable_coverage(brief, ws, product_codes=["30325"], top_n=5)
    assert "missing_sku_evidence_columns" not in cov["gaps"]
    assert cov["ok"] is True
    assert any(c.startswith("fewer_than_requested") for c in cov["caveats"])


def test_brain_runtime_blocks_km_filter(tmp_path):
    def _tbl(name: str, cols: list[str]) -> TableMeta:
        return TableMeta(name=name, columns=[ColumnMeta(name=c, data_type="varchar") for c in cols])

    catalog = SchemaCatalog(
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

    class _Gw:
        def execute_readonly(self, sql, acl, *, target_db="db2"):
            if "SKU_DEF" in sql.upper():
                rows = [{"SKU_ID": "ID1", "SKU_CODE": "30344", "FULL_NAME": "KM-Item"}]
            else:
                rows = [
                    {
                        "TRANS_NUM": "B1",
                        "TRAN_DATE": "2026-07-02",
                        "TRAN_TIME": "10:00",
                        "STK_ID": 1,
                        "SKU_ID": "ID1",
                        "TRANS_CODE": "221",
                        "QTY": 1,
                        "AMOUNT": 0,
                    }
                ]
            return {"rows": rows, "columns": list(rows[0].keys()), "row_count": len(rows)}

    policy = PolicyEngine(catalog, allowed_tables=list(catalog.tables()))
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    toolkit = DataFetchToolkit(
        sql_gateway=_Gw(),
        policy=policy,
        acl=SqlAclContext(actor_id="t", allowed_tables=list(catalog.tables()), tool_grants=["tool:*"]),
        working_set=ws,
        max_rows=100,
    )

    class _Planner:
        def __init__(self) -> None:
            self.tokens = 0
            self._i = 0

        def next_decision(self, state):
            self._i += 1
            if self._i == 1:
                return {
                    "phase": "ground",
                    "thought": "resolve",
                    "decision": "fetch",
                    "tool": {
                        "tool_id": "resolve_products",
                        "args": {"codes": ["30344"]},
                        "save_as": "products",
                    },
                }
            if self._i == 2:
                return {
                    "phase": "assemble",
                    "thought": "guess KM = gift",
                    "decision": "run_op",
                    "op": {
                        "op_id": "filter_rows",
                        "dataset": "products",
                        "args": {
                            "conditions": [
                                {"column": "FULL_NAME", "operator": "contains", "value": "KM"}
                            ],
                            "save_as": "filtered",
                        },
                    },
                }
            return {
                "phase": "deliver",
                "thought": "stop",
                "decision": "finalize",
                "status": "partial",
                "caveats": ["stopped_after_block"],
            }

    payload = brain.run_data_agent_brain(
        brief=AnalysisBrief(
            intent="30344 dang qua tang",
            filters={"product_code": "30344", "product_type": "quà tặng"},
            time_range=TimeRange(start="2026-07-01", end="2026-07-06"),
        ),
        out_dir=str(tmp_path / "out"),
        fetch_toolkit=toolkit,
        working_set=ws,
        planner=_Planner(),
        use_stub=False,
        max_planner_turns=6,
    )
    obs = payload.get("observations") or []
    assert any(o.get("error") == "blocked_name_type_guess" for o in obs)
    assert "product_type_unverified" in (payload.get("caveats") or [])


def test_brain_rejects_nonblocking_type_clarify_when_codes_present(tmp_path):
    def _tbl(name: str, cols: list[str]) -> TableMeta:
        return TableMeta(name=name, columns=[ColumnMeta(name=c, data_type="varchar") for c in cols])

    catalog = SchemaCatalog(
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

    class _Gw:
        def execute_readonly(self, sql, acl, *, target_db="db2"):
            u = sql.upper()
            if "SKU_DEF" in u:
                rows = [{"SKU_ID": "ID1", "SKU_CODE": "30344", "FULL_NAME": "KM-Item"}]
            elif "TRANSHDR" in u:
                rows = [
                    {
                        "TRANS_NUM": "B1",
                        "TRAN_DATE": "2026-07-02",
                        "TRAN_TIME": "10:00",
                        "STK_ID": 1,
                        "TRANS_CODE": "101",
                        "AMOUNT": 700000,
                    }
                ]
            else:
                rows = [
                    {
                        "TRANS_NUM": "B1",
                        "TRAN_DATE": "2026-07-02",
                        "TRAN_TIME": "10:00",
                        "STK_ID": 1,
                        "SKU_ID": "ID1",
                        "TRANS_CODE": "221",
                        "QTY": 1,
                        "AMOUNT": 0,
                    }
                ]
            return {"rows": rows, "columns": list(rows[0].keys()), "row_count": len(rows)}

    policy = PolicyEngine(catalog, allowed_tables=list(catalog.tables()))
    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    toolkit = DataFetchToolkit(
        sql_gateway=_Gw(),
        policy=policy,
        acl=SqlAclContext(actor_id="t", allowed_tables=list(catalog.tables()), tool_grants=["tool:*"]),
        working_set=ws,
        max_rows=100,
    )

    class _Planner:
        def __init__(self) -> None:
            self.tokens = 0
            self._i = 0

        def next_decision(self, state):
            self._i += 1
            if self._i == 1:
                return {
                    "phase": "ground",
                    "thought": "resolve codes",
                    "decision": "fetch",
                    "tool": {
                        "tool_id": "resolve_products",
                        "args": {"codes": ["30344"]},
                        "save_as": "products",
                    },
                }
            # Decorative clarify about KM/gift — must be rejected at runtime.
            return {
                "phase": "ground",
                "thought": "FULL_NAME has KM; clarify if KM means gift/quà tặng",
                "decision": "clarify",
                "clarification_request": {
                    "reason": "Is KM a gift product type?",
                    "questions": [{"id": "km_gift", "prompt": "KM = quà tặng?"}],
                },
            }

    payload = brain.run_data_agent_brain(
        brief=AnalysisBrief(
            intent="30344 dang qua tang lay 5 bill",
            filters={"product_code": "30344", "product_type": "quà tặng", "min_bill_value": 600000},
            time_range=TimeRange(start="2026-07-01", end="2026-07-06"),
            output_format=["excel"],
        ),
        out_dir=str(tmp_path / "out"),
        fetch_toolkit=toolkit,
        working_set=ws,
        planner=_Planner(),
        use_stub=False,
        max_planner_turns=8,
    )
    assert payload.get("action") != "suggest_clarify"
    obs = payload.get("observations") or []
    assert any(o.get("error") == "clarify_rejected_codes_sufficient" for o in obs)
    assert any(o.get("tool_id") == "query_rows" and o.get("ok") for o in obs)


def test_is_nonblocking_type_clarify_markers_and_hard_blockers():
    codes = ["30325"]
    assert is_nonblocking_type_clarify(
        product_codes=codes,
        thought="ITEM_TYPE empty sparse_column_unusable — ask user about gift type",
        decision={"decision": "clarify", "reason": "filter ITEM_TYPE"},
    )
    assert is_nonblocking_type_clarify(
        product_codes=codes,
        thought="confirm product_type quà tặng",
        product_type_soft="quà tặng",
    )
    assert is_nonblocking_type_clarify(
        product_codes=codes,
        thought="KM in FULL_NAME — is this gift?",
        decision={"clarification_request": {"reason": "KM gift type?"}},
    )
    # Hard blockers must still clarify.
    assert not is_nonblocking_type_clarify(
        product_codes=codes,
        thought="missing time_range for analysis window",
        decision={"reason": "thiếu ngày"},
    )
    assert not is_nonblocking_type_clarify(
        product_codes=[],
        thought="ITEM_TYPE empty",
    )
    # Join AMOUNT collision / header-vs-line is non-blocking when codes pin SKUs.
    assert is_nonblocking_type_clarify(
        product_codes=codes,
        thought=(
            "filter_rows failed missing AMOUNT; ask whether header amount or "
            "line amount (AMOUNT_x vs AMOUNT_y)"
        ),
        decision={"decision": "clarify", "reason": "column name collisions"},
    )
    # Display-name "codes" / failed resolve must escalate to UI.
    assert not is_nonblocking_type_clarify(
        product_codes=["bánh chưng nương bắc"],
        thought="resolve_products returned 0 rows for product name",
    )
    assert not is_nonblocking_type_clarify(
        product_codes=codes,
        thought="product name not found",
        resolved_sku_count=0,
    )


def test_rank_bill_frame_scopes_to_product_codes(tmp_path):
    from project_core.domain.analysis.data_agent_guards import rank_bill_frame_for_export

    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    out = tmp_path / "out"
    out.mkdir()
    ws.save_frame(
        "joined",
        pd.DataFrame(
            {
                "TRANS_NUM": [f"B{i}" for i in range(20)],
                "SKU_ID": ["290003034400"] * 8 + ["OTHER"] * 12,
                "TRAN_DATE": ["2026-07-0" + str((i % 6) + 1) for i in range(20)],
            }
        ),
        source="join",
        role="fact",
    )
    ws.save_frame(
        "resolve_products",
        pd.DataFrame({"SKU_ID": ["290003034400"], "SKU_CODE": ["00030344"]}),
        source="resolve",
        role="dim",
    )
    ref = rank_bill_frame_for_export(
        ws,
        source_ref="joined",
        top_n=5,
        out_dir=out,
        partition_by=["SKU_ID"],
        product_codes=["0030344"],
    )
    df = ws.get(ref).frame()
    assert set(df["SKU_ID"].astype(str)) == {"290003034400"}
    assert len(df) <= 5


def test_coverage_flags_extra_skus_outside_brief():
    from project_core.domain.analysis.data_agent_guards import assess_deliverable_coverage

    ws = DatasetWorkingSet()
    ws.save_frame(
        "resolve_products",
        pd.DataFrame({"SKU_ID": ["GIFT1", "GIFT2"], "SKU_CODE": ["A", "B"]}),
        source="resolve",
        role="dim",
    )
    ws.save_frame(
        "bills_top_n",
        pd.DataFrame(
            {
                "TRANS_NUM": [f"B{i}" for i in range(30)],
                "SKU_ID": ["GIFT1"] * 5 + ["GIFT2"] * 5 + [f"X{i}" for i in range(20)],
                "TRAN_DATE": ["2026-07-01"] * 30,
                "QTY": [1] * 30,
            }
        ),
        source="top_n_per_group",
        role="fact",
        op_id="top_n_per_group",
    )
    brief = AnalysisBrief(intent="top 5", filters={"product_code": ["A", "B"], "top_n": 5})
    cov = assess_deliverable_coverage(brief, ws, product_codes=["A", "B"], top_n=5)
    assert not cov["ok"]
    assert any(str(g).startswith("product_scope_extra_skus") for g in cov["gaps"])



def test_prefer_export_prefers_expanded_bill_lines():
    ws = DatasetWorkingSet()
    ws.save_frame(
        'resolve_products',
        pd.DataFrame({'SKU_ID': ['S1'], 'SKU_CODE': ['0001']}),
        source='resolve_products',
        role='catalog',
    )
    ws.save_frame(
        'sale_lines',
        pd.DataFrame(
            {
                'TRANS_NUM': ['T1', 'T2'],
                'SKU_ID': ['S1', 'S1'],
                'CARD_ID': ['C1', 'C2'],
                'CUST_NAME': ['A', 'B'],
            }
        ),
        source='query_rows',
        role='fact',
    )
    ws.save_frame(
        'sale_lines_all_bill_lines',
        pd.DataFrame(
            {
                'TRANS_NUM': ['T1', 'T1', 'T2'],
                'SKU_ID': ['S1', 'S9', 'S1'],
                'CARD_ID': ['C1', 'C1', 'C2'],
            }
        ),
        source='query_rows',
        role='fact',
    )
    chosen = prefer_export_dataset_ref(ws, needs_bill=True, product_codes=['0001'])
    assert chosen == 'sale_lines_all_bill_lines'
