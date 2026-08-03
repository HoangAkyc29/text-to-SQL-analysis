"""Export helpers — split_by_column + loyalty rich report sections."""
from __future__ import annotations

from datetime import date

import pandas as pd

from app.export.rich_report import build_loyalty_rich_report, build_orders_rich_report
from app.export.splitters import PointBucket, assign_bucket, split_by_column, split_by_point_buckets


def test_assign_bucket_boundaries():
    buckets = [
        PointBucket(label="0-200", lo=0, hi=200),
        PointBucket(label="200-500", lo=200, hi=500),
        PointBucket(label=">=500", lo=500, hi=None),
    ]
    assert assign_bucket(0, buckets) == "0-200"
    assert assign_bucket(199.9, buckets) == "0-200"
    assert assign_bucket(200, buckets) == "200-500"
    assert assign_bucket(500, buckets) == ">=500"
    assert assign_bucket(9000, buckets) == ">=500"


def test_split_by_point_buckets_no_overlap():
    buckets = [
        PointBucket(label="lo", lo=0, hi=10),
        PointBucket(label="hi", lo=10, hi=None),
    ]
    df = pd.DataFrame({"points": [0, 9.9, 10, 50], "CARD_ID": list("ABCD")})
    parts = split_by_point_buckets(df, buckets, col="points")
    assert set(parts["lo"]["CARD_ID"]) == {"A", "B"}
    assert set(parts["hi"]["CARD_ID"]) == {"C", "D"}


def test_split_by_column_groups_blank_as_empty():
    df = pd.DataFrame(
        {
            "CARD_ID": ["A", "A", "B", ""],
            "SKU_ID": ["1", "2", "1", "3"],
            "v": [1, 2, 3, 4],
        }
    )
    parts = split_by_column(df, "CARD_ID")
    assert set(parts.keys()) == {"A", "B", "EMPTY"}
    assert len(parts["A"]) == 2
    assert len(parts["B"]) == 1
    assert len(parts["EMPTY"]) == 1


def test_build_loyalty_rich_report_listings_after_summary():
    customers = pd.DataFrame(
        {
            "CARD_ID": ["E1", "E2"],
            "NAME_U": ["A", "B"],
            "points": [1.0, 12.0],
            "total_value": [50_000.0, 600_000.0],
            "bill_count": [1, 2],
            "SEX": ["F", "M"],
            "BIRTHDAY": ["1990-07-01", "1985-01-01"],
            "STK_ID": ["10001", "10001"],
        }
    )
    cohort = pd.DataFrame(
        {
            "STK_ID": ["10001", "10001"],
            "TRANS_NUM": ["T1", "T2"],
            "CARD_ID": ["E1", "E2"],
            "SKU_ID": ["1001", "1002"],
            "FULL_NAME_U": ["Sữa", "Bánh"],
            "line_total": [50_000.0, 300_000.0],
            "TRAN_DATE": [date(2026, 7, 1), date(2026, 7, 2)],
            "TRAN_TIME": ["10:00", "11:00"],
            "IDX": [1, 1],
        }
    )
    text = "\n".join(
        build_loyalty_rich_report(
            customers=customers,
            cohort_lines=cohort,
            options=["count", "by_points", "by_store", "by_age", "by_hour"],
        )
    )
    i_summary = text.index("TÓM TẮT")
    i_sku = text.index("TOP MẶT HÀNG")
    i_detail = text.index("CHI TIẾT TỪNG THẺ")
    assert i_summary < i_sku < i_detail


def test_build_orders_rich_report_listings_after_summary():
    matched = pd.DataFrame(
        {
            "STK_ID": ["10001"],
            "TRANS_NUM": ["T1"],
            "CARD_ID": ["E1"],
            "SKU_ID": ["1001"],
            "line_total": [10.0],
        }
    )
    bill = pd.DataFrame(
        {
            "STK_ID": ["10001", "10001"],
            "TRANS_NUM": ["T1", "T1"],
            "CARD_ID": ["E1", "E1"],
            "SKU_ID": ["1001", "1002"],
            "FULL_NAME_U": ["A", "B"],
            "line_total": [10.0, 20.0],
            "TRAN_DATE": [date(2026, 7, 1), date(2026, 7, 1)],
            "TRAN_TIME": ["10:00", "10:00"],
            "IDX": [1, 2],
            "NAME_U": ["Khách", "Khách"],
        }
    )
    text = "\n".join(
        build_orders_rich_report(
            title="TEST",
            matched_lines=matched,
            bill_lines=bill,
            exclude_skus=["1001"],
            include_per_bill_detail=True,
        )
    )
    i_summary = text.index("TÓM TẮT")
    i_listing = text.index("CHI TIẾT LIỆT KÊ")
    i_sku = text.index("TẦN SUẤT MẶT HÀNG TỔNG HỢP")
    assert i_summary < i_listing < i_sku


def test_build_orders_rich_report_excludes_seed_skus():
    matched = pd.DataFrame(
        {
            "STK_ID": ["10001"],
            "TRANS_NUM": ["T1"],
            "CARD_ID": ["E1"],
            "SKU_ID": ["1001"],
            "line_total": [10.0],
        }
    )
    bill = pd.DataFrame(
        {
            "STK_ID": ["10001", "10001"],
            "TRANS_NUM": ["T1", "T1"],
            "CARD_ID": ["E1", "E1"],
            "SKU_ID": ["1001", "2001"],
            "SKU_CODE": ["SP001", "QT001"],
            "FULL_NAME_U": ["Seed", "Kèm"],
            "line_total": [10.0, 5.0],
            "TRAN_DATE": [date(2026, 7, 1), date(2026, 7, 1)],
            "TRAN_TIME": ["10", "10"],
        }
    )
    lines = build_orders_rich_report(
        title="T",
        matched_lines=matched,
        bill_lines=bill,
        exclude_skus=["1001"],
        exclude_label="SKU lọc",
        include_per_bill_detail=True,
        per_card_limit=None,
    )
    text = "\n".join(lines)
    assert "QT001" in text or "Kèm" in text
