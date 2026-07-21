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
            "ItemCode": ["A-17", "B-29", "C-41"],
            "TotalQuantity": [2, 3, 4],
            "ReceiptNumber": ["R1", "R2", "R3"],
            "ReceiptAmount": [1_500, 1_700, 1_900],
            "EventDate": pd.to_datetime(["2030-02-01", "2030-02-02", "2030-02-03"]),
            "SegmentGroup": ["segment-x", "segment-x", "segment-x"],
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
                "metrics": ["quantity"],
                "dimensions": ["product", "transaction"],
                "filters": {
                    "product_code": ["A-17", "B-29", "C-41"],
                    "min_transaction_value": 1_500,
                    "category": "segment-x",
                },
                "time_range": {
                    "start": "2030-02-01",
                    "end": "2030-02-03",
                    "grain": "day",
                },
                "requirements": [
                    {"requirement_id": "metric:0", "kind": "metric", "key": "quantity", "source": "explicit", "required": True, "value": "quantity"},
                    {"requirement_id": "dimension:0", "kind": "dimension", "key": "product", "source": "explicit", "required": True, "value": "product"},
                    {"requirement_id": "dimension:1", "kind": "dimension", "key": "transaction", "source": "explicit", "required": True, "value": "transaction"},
                    {"requirement_id": "filter:0", "kind": "filter", "key": "product_code", "source": "explicit", "required": True, "value": ["A-17", "B-29", "C-41"]},
                    {"requirement_id": "filter:1", "kind": "filter", "key": "min_transaction_value", "source": "explicit", "required": True, "value": 1_500},
                    {"requirement_id": "filter:2", "kind": "filter", "key": "category", "source": "explicit", "required": True, "value": "segment-x"},
                    {"requirement_id": "time:0", "kind": "time", "key": "time_range", "source": "explicit", "required": True, "value": {"start": "2030-02-01", "end": "2030-02-03", "grain": "day"}},
                    {"requirement_id": "ranking:0", "kind": "ranking", "key": "top_n", "source": "explicit", "required": True, "value": {"limit": 1, "partition_by": "product", "order_by": "time", "direction": "desc"}},
                ],
            },
            "semantic_labels": [
                {"output_name": "ItemCode", "semantic_key": "product_code"},
                {"output_name": "TotalQuantity", "semantic_key": "quantity"},
                {"output_name": "ReceiptNumber", "semantic_key": "transaction_number"},
                {"output_name": "ReceiptAmount", "semantic_key": "transaction_amount"},
                {"output_name": "SegmentGroup", "semantic_key": "category"},
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
    assert result.result["ranking_missing"] == []


def test_brief_coverage_rejects_schema_only_filter_and_time_claims(tmp_path):
    frame = pd.DataFrame(
        {
            "ItemCode": ["X-1"],
            "Quantity": [2],
            "TransactionNumber": [9_999_999],
            "EventDate": pd.to_datetime(["2031-01-01"]),
        }
    )
    source = tmp_path / "wrong-evidence.parquet"
    frame.to_parquet(source, index=False)
    working_set = DatasetWorkingSet.from_manifest(
        {"queries": [{"path": str(source), "ref": "q0", "row_count": 1}]},
        [{"role": "main"}],
        work_dir=tmp_path / "ws-negative",
    )
    result = execute_op(
        working_set,
        "match_brief_coverage",
        {
            "brief": {
                "requirements": [
                    {"requirement_id": "filter:0", "kind": "filter", "key": "product_code", "source": "explicit", "required": True, "value": ["Y-2"]},
                    {"requirement_id": "filter:1", "kind": "filter", "key": "min_transaction_value", "source": "explicit", "required": True, "value": 5_000},
                    {"requirement_id": "time:0", "kind": "time", "key": "time_range", "source": "explicit", "required": True, "value": {"start": "2030-01-01", "end": "2030-01-31"}},
                ]
            },
            "semantic_labels": [
                {"output_name": "ItemCode", "semantic_key": "product_code"},
                {"output_name": "TransactionNumber", "semantic_key": "transaction_number"},
                {"output_name": "EventDate", "semantic_key": "event_date"},
            ],
        },
        out_dir=tmp_path / "out-negative",
    )
    assert result.result["filters_missing"] == [
        "product_code",
        "min_transaction_value",
    ]
    assert result.result["time_covered"] is False
    assert result.result["ok"] is False


def test_brief_coverage_checks_partitioned_ranking_order(tmp_path):
    ordered = pd.DataFrame(
        {
            "SKU_CODE": ["A-1", "A-1", "B-2", "B-2"],
            "TRAN_DATE": pd.to_datetime(
                ["2033-04-03", "2033-04-03", "2033-04-02", "2033-04-01"]
            ),
            "TRAN_TIME": ["18:00", "09:00", "12:00", "08:00"],
        }
    )

    def _check(frame, name):
        source = tmp_path / f"{name}.parquet"
        frame.to_parquet(source, index=False)
        working_set = DatasetWorkingSet.from_manifest(
            {"queries": [{"path": str(source), "ref": "q0", "row_count": len(frame)}]},
            [{"role": "main"}],
            work_dir=tmp_path / name,
        )
        return execute_op(
            working_set,
            "match_brief_coverage",
            {
                "brief": {
                    "requirements": [
                        {
                            "requirement_id": "ranking:0",
                            "kind": "ranking",
                            "key": "recent_rows",
                            "source": "explicit",
                            "required": True,
                            "value": {
                                "limit": 2,
                                "partition_by": "product",
                                "order_by": "transaction_date",
                                "direction": "desc",
                            },
                        }
                    ]
                }
            },
            out_dir=tmp_path / f"{name}-out",
        ).result

    assert _check(ordered, "ordered")["ranking_missing"] == []
    unsorted = ordered.iloc[[1, 0, 2, 3]].reset_index(drop=True)
    assert _check(unsorted, "unsorted")["ranking_missing"] == ["ranking:0"]


def test_execute_op_repairs_common_cast_argument_aliases(tmp_path):
    frame = pd.DataFrame({"amount": ["1.5", "2.5"]})
    source = tmp_path / "cast-alias.parquet"
    frame.to_parquet(source, index=False)
    working_set = DatasetWorkingSet.from_manifest(
        {"queries": [{"path": str(source), "ref": "q0", "row_count": 2}]},
        [{"role": "main"}],
        work_dir=tmp_path / "cast-ws",
    )
    result = execute_op(
        working_set,
        "cast_column",
        {
            "dataset": "q0",
            "columns": ["amount"],
            "dtype": "float",
            "save_as": "casted",
        },
        out_dir=tmp_path / "cast-out",
    )
    assert result.status == "ok"
    assert result.result["arg_repairs"] == ["columns->column", "dtype->to"]
    assert str(working_set.get("casted").frame()["amount"].dtype) == "float64"
