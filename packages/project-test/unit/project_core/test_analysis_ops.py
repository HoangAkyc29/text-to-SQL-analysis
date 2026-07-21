"""Unit tests for Agent IV analysis ops catalog."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from project_core.domain.analysis.ops import DatasetWorkingSet, execute_op, list_op_ids
from project_core.domain.analysis.ops.expr_dsl import eval_column_expr


@pytest.fixture
def ws(tmp_path):
    df = pd.DataFrame(
        {
            "SKU_CODE": ["A", "A", "B", "B", "B"],
            "QTY": [1, 2, 3, 4, 5],
            "BillAmount": [100, 700000, 800000, 500, 900000],
            "TRAN_DATE": pd.to_datetime(
                ["2026-07-01", "2026-07-02", "2026-07-03", "2026-07-04", "2026-07-05"]
            ),
        }
    )
    path = tmp_path / "q0.parquet"
    df.to_parquet(path, index=False)
    out = DatasetWorkingSet.from_manifest(
        {"queries": [{"path": str(path), "ref": "q0", "row_count": 5}]},
        [{"role": "main"}],
        work_dir=tmp_path / "ws",
    )
    return out, tmp_path / "out"


def test_catalog_has_expected_ops():
    ids = set(list_op_ids())
    for required in {
        "filter_rows",
        "groupby_agg",
        "top_n_per_group",
        "export_csv",
        "export_excel",
        "match_brief_coverage",
    }:
        assert required in ids
    assert len(ids) >= 35


def test_filter_and_groupby_export(ws):
    working, out_dir = ws
    out_dir.mkdir(parents=True)
    r = execute_op(
        working,
        "filter_rows",
        {"dataset": "q0", "save_as": "ge600k", "column": "BillAmount", "op": "gte", "value": 600000},
        out_dir=out_dir,
    )
    assert r.status == "ok"
    assert r.result["row_count"] == 3
    r2 = execute_op(
        working,
        "groupby_agg",
        {
            "dataset": "ge600k",
            "save_as": "by_sku",
            "by": ["SKU_CODE"],
            "aggs": [{"column": "QTY", "fn": "sum", "as": "qty_sum"}],
        },
        out_dir=out_dir,
    )
    assert r2.status == "ok"
    assert r2.result["row_count"] == 2
    r3 = execute_op(
        working,
        "export_csv",
        {"dataset": "by_sku", "filename": "summary.csv"},
        out_dir=out_dir,
    )
    assert r3.status == "ok"
    assert Path(r3.result["path"]).exists()
    assert working.artifact_paths


def test_top_n_per_group(ws):
    working, out_dir = ws
    out_dir.mkdir(parents=True)
    r = execute_op(
        working,
        "top_n_per_group",
        {
            "dataset": "q0",
            "save_as": "top2",
            "partition_by": ["SKU_CODE"],
            "order_by": ["TRAN_DATE"],
            "ascending": False,
            "n": 2,
        },
        out_dir=out_dir,
    )
    assert r.status == "ok"
    assert r.result["row_count"] == 4  # 2 for A, 2 for B (B has 3)


def test_expr_dsl_add_column(ws):
    working, out_dir = ws
    out_dir.mkdir(parents=True)
    r = execute_op(
        working,
        "add_column_expr",
        {"dataset": "q0", "save_as": "with_dbl", "name": "QTY2", "expr": "QTY * 2"},
        out_dir=out_dir,
    )
    assert r.status == "ok"
    assert "QTY2" in r.result["columns"]
    df = working.get("with_dbl").frame()
    assert int(df["QTY2"].iloc[0]) == 2


def test_expr_rejects_import():
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(Exception):
        eval_column_expr(df, "__import__('os')")


def test_analyze_datasets_fallback_exports(tmp_path):
    from project_core.domain.analysis.iv_analyzer import analyze_datasets
    from project_core.domain.contracts.brief import AnalysisBrief

    df = pd.DataFrame({"SKU": ["x"], "AMT": [10]})
    path = tmp_path / "q.parquet"
    df.to_parquet(path, index=False)
    out = tmp_path / "out"
    out.mkdir()
    payload = analyze_datasets(
        brief=AnalysisBrief(intent="test", metrics=["AMT"], dimensions=["SKU"], output_format=["excel"]),
        manifest={"queries": [{"path": str(path), "row_count": 1}]},
        profile={"row_count": 1},
        out_dir=str(out),
        query_meta=[{"role": "main"}],
    )
    assert payload["action"] in {"complete", "partial"}
    assert payload.get("artifact_paths")


def test_brief_coverage_uses_semantics_and_filter_value_evidence(tmp_path):
    frame = pd.DataFrame(
        {
            "SKU_CODE": ["0030344", "0030348", "0030355"],
            "TOTAL_GIFT_QTY": [2, 3, 4],
            "TRANS_NUM": ["B1", "B2", "B3"],
            "BILL_AMOUNT": [600_000, 700_000, 800_000],
            "TRAN_DATE": pd.to_datetime(["2026-07-01", "2026-07-02", "2026-07-03"]),
            "GRP_NAME": ["quà tặng", "quà tặng", "quà tặng"],
        }
    )
    source = tmp_path / "coverage.parquet"
    frame.to_parquet(source, index=False)
    working_set = DatasetWorkingSet.from_manifest(
        {"queries": [{"path": str(source), "ref": "q0", "row_count": 3}]},
        [{"role": "main"}],
        work_dir=tmp_path / "ws",
    )
    result = execute_op(
        working_set,
        "match_brief_coverage",
        {
            "brief": {
                "metrics": ["quantity", "min_bill_value"],
                "dimensions": ["product", "transaction"],
                "filters": {
                    "product_code": ["0030344", "0030348", "0030355"],
                    "min_bill_value": 600_000,
                    "category": "quà tặng",
                },
                "time_range": {
                    "start": "2026-07-01",
                    "end": "2026-07-06",
                    "grain": "day",
                },
            },
            "semantic_labels": [
                {"output_name": "SKU_CODE", "semantic_key": "sku_code"},
                {"output_name": "TOTAL_GIFT_QTY", "semantic_key": "gift_qty"},
                {"output_name": "TRANS_NUM", "semantic_key": "transaction_number"},
                {"output_name": "BILL_AMOUNT", "semantic_key": "transaction_amount"},
                {"output_name": "GRP_NAME", "semantic_key": "product_group"},
            ],
        },
        out_dir=tmp_path / "out",
    )
    assert result.status == "ok"
    assert result.result["ok"] is True
    assert result.result["metrics_missing"] == []
    assert result.result["dimensions_missing"] == []
    assert result.result["filters_missing"] == []
    assert result.result["time_covered"] is True
