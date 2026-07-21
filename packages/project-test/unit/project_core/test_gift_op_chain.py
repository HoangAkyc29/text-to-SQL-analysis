"""Gift-shaped op compose: filter >=600k -> groupby -> top_n_per_group -> excel."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from project_core.domain.analysis.ops import DatasetWorkingSet, execute_op


def test_gift_shaped_op_chain(tmp_path):
    rows = []
    for sku in ("0030344", "0030348", "0030355"):
        for i in range(6):
            rows.append(
                {
                    "SKU_CODE": sku,
                    "QTY": 1,
                    "BillAmount": 100000 if i == 0 else 700000 + i * 1000,
                    "TRAN_DATE": pd.Timestamp("2026-07-01") + pd.Timedelta(days=i),
                    "TRANS_ID": f"{sku}-{i}",
                }
            )
    path = tmp_path / "q0.parquet"
    pd.DataFrame(rows).to_parquet(path, index=False)
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    ws = DatasetWorkingSet.from_manifest(
        {"queries": [{"path": str(path), "ref": "q0", "row_count": len(rows)}]},
        [{"role": "main"}],
        work_dir=tmp_path / "ws",
    )
    assert (
        execute_op(
            ws,
            "filter_rows",
            {"dataset": "q0", "save_as": "ge600k", "column": "BillAmount", "op": "gte", "value": 600000},
            out_dir=out_dir,
        ).status
        == "ok"
    )
    assert (
        execute_op(
            ws,
            "groupby_agg",
            {
                "dataset": "ge600k",
                "save_as": "qty_by_sku",
                "by": ["SKU_CODE"],
                "aggs": [{"column": "QTY", "fn": "sum", "as": "gift_qty"}],
            },
            out_dir=out_dir,
        ).status
        == "ok"
    )
    assert (
        execute_op(
            ws,
            "top_n_per_group",
            {
                "dataset": "ge600k",
                "save_as": "top5",
                "partition_by": ["SKU_CODE"],
                "order_by": ["TRAN_DATE"],
                "ascending": False,
                "n": 5,
            },
            out_dir=out_dir,
        ).status
        == "ok"
    )
    assert len(ws.get("top5").frame()) == 15
    r = execute_op(
        ws,
        "export_excel",
        {
            "filename": "gift.xlsx",
            "sheets": {"qty": "qty_by_sku", "bills": "top5"},
        },
        out_dir=out_dir,
    )
    assert r.status == "ok"
    assert Path(r.result["path"]).exists()
