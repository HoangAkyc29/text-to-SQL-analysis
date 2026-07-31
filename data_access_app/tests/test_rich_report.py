"""Unit tests for rich report helpers (no DB)."""
from __future__ import annotations

import pandas as pd

from app.export.rich_report import (
    bill_totals,
    build_orders_rich_report,
    sku_frequency,
    store_summary_frame,
)


def _sample_lines() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "STK_ID": "10001",
                "TRANS_NUM": "T1",
                "CARD_ID": "E1",
                "SKU_ID": "S_SEED",
                "FULL_NAME_U": "Seed",
                "line_total": 100.0,
                "TRAN_DATE": "2026-07-01",
                "TRAN_TIME": "10:00",
                "IDX": 1,
            },
            {
                "STK_ID": "10001",
                "TRANS_NUM": "T1",
                "CARD_ID": "E1",
                "SKU_ID": "S_OTHER",
                "FULL_NAME_U": "Other",
                "line_total": 50.0,
                "TRAN_DATE": "2026-07-01",
                "TRAN_TIME": "10:00",
                "IDX": 2,
            },
            {
                "STK_ID": "10004",
                "TRANS_NUM": "T2",
                "CARD_ID": "E2",
                "SKU_ID": "S_OTHER",
                "FULL_NAME_U": "Other",
                "line_total": 200.0,
                "TRAN_DATE": "2026-07-02",
                "TRAN_TIME": "15:00",
                "IDX": 1,
            },
        ]
    )


def test_store_summary_so_tong_tb():
    summary = store_summary_frame(_sample_lines())
    assert list(summary["STK_ID"].astype(str)) == ["10001", "10004"]
    row1 = summary.loc[summary["STK_ID"].astype(str) == "10001"].iloc[0]
    assert int(row1["SO_GIAO_DICH"]) == 1
    assert float(row1["TONG_GIA_TRI"]) == 150.0
    assert float(row1["TB_GIA_TRI"]) == 150.0


def test_sku_frequency_excludes_seed():
    freq = sku_frequency(_sample_lines(), exclude_skus=["S_SEED"])
    assert list(freq["SKU_ID"].astype(str)) == ["S_OTHER"]
    assert int(freq.iloc[0]["SO_LAN"]) == 2


def test_bill_totals():
    bills = bill_totals(_sample_lines())
    assert len(bills) == 2
    t1 = bills.loc[bills["TRANS_NUM"] == "T1"].iloc[0]
    assert float(t1["bill_total"]) == 150.0


def test_build_orders_report_contains_sections():
    lines = _sample_lines()
    text = "\n".join(
        build_orders_rich_report(
            title="Test",
            matched_lines=lines.loc[lines["SKU_ID"] == "S_SEED"],
            bill_lines=lines,
            exclude_skus=["S_SEED"],
            exclude_label="SKU đang tìm",
            include_per_bill_detail=True,
            per_card_limit=10,
        )
    )
    assert "THỐNG KÊ THEO TỪNG SIÊU THỊ" in text
    assert "TẦN SUẤT MẶT HÀNG" in text
    assert "S_OTHER" in text
    assert "AMOUNT + SURPLUS + VAT_AMT" in text
    assert "orders/matched=" in text


def test_build_orders_report_full_detail_when_no_card_limit():
    lines = _sample_lines()
    # Many unique cards would normally truncate — None must keep detail
    text = "\n".join(
        build_orders_rich_report(
            title="Full",
            matched_lines=lines,
            bill_lines=lines,
            include_per_bill_detail=True,
            per_card_limit=None,
        )
    )
    assert "bỏ qua chi tiết từng thẻ" not in text
    assert "CARD_ID : E1" in text
    assert "CARD_ID : E2" in text
