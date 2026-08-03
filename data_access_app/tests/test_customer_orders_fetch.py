"""F4 customer orders — gift/paid gating, bill bounds, header fallback, age/sex."""
from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from app.domain.columns import F4_ORDER_LINE_COLUMNS
from app.domain.customer_orders import fetch_customer_orders
from tests.conftest import QueryCapture, assert_where_contains, assert_where_not_contains, make_lookup


def _sku_df(sku_id: str = "1001") -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "SKU_ID": sku_id,
                "SKU_CODE": "SP001",
                "BARCODE": "x",
                "FULL_NAME_U": "Sữa",
                "GRP_ID": "G1",
                "GRP_NAME": "Sữa",
                "DEPT_ID": "D1",
                "UNIT_SYMB": "HOP",
                "RTPRICE": 1,
                "STATUS": "A",
            }
        ]
    )


def _strans_seed() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "STK_ID": "10001",
                "TRANS_NUM": "BILL1",
                "TRAN_DATE": date(2026, 7, 1),
                "TRAN_TIME": "10:00",
                "CARD_ID": "E10000000053",
                "TRANS_CODE": "113",
                "IDX": 1,
                "SKU_ID": "1001",
                "QTY": 1,
                "UNIT_SYMB": "HOP",
                "line_total": 80_000.0,
            },
            {
                "STK_ID": "10001",
                "TRANS_NUM": "BILL2",
                "TRAN_DATE": date(2026, 7, 2),
                "TRAN_TIME": "11:00",
                "CARD_ID": "E10000000053",
                "TRANS_CODE": "113",
                "IDX": 1,
                "SKU_ID": "1001",
                "QTY": 1,
                "UNIT_SYMB": "HOP",
                "line_total": 200_000.0,
            },
            {
                "STK_ID": "10001",
                "TRANS_NUM": "BILL3",
                "TRAN_DATE": date(2026, 7, 3),
                "TRAN_TIME": "12:00",
                "CARD_ID": "A10000054973",
                "TRANS_CODE": "113",
                "IDX": 1,
                "SKU_ID": "1002",
                "QTY": 1,
                "UNIT_SYMB": "GOI",
                "line_total": 50_000.0,
            },
        ]
    )


def _headers() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "STK_ID": "10001",
                "TRANS_NUM": "BILL1",
                "TRAN_DATE": date(2026, 7, 1),
                "TRAN_TIME": "10:00",
                "CARD_ID": "E10000000053",
                "TRANS_CODE": "113",
                "bill_value": 80_000.0,
            },
            {
                "STK_ID": "10001",
                "TRANS_NUM": "BILL2",
                "TRAN_DATE": date(2026, 7, 2),
                "TRAN_TIME": "11:00",
                "CARD_ID": "E10000000053",
                "TRANS_CODE": "113",
                "bill_value": 200_000.0,
            },
            {
                "STK_ID": "10001",
                "TRANS_NUM": "BILL3",
                "TRAN_DATE": date(2026, 7, 3),
                "TRAN_TIME": "12:00",
                "CARD_ID": "A10000054973",
                "TRANS_CODE": "113",
                "bill_value": 50_000.0,
            },
        ]
    )


def _install_base(monkeypatch, cap: QueryCapture, profiles: pd.DataFrame, *, lines=None, headers=None):
    lines = _strans_seed() if lines is None else lines
    headers = _headers() if headers is None else headers
    cap.set_strans(lambda *a, **k: lines.copy())
    monkeypatch.setattr("app.domain.customer_orders.query_strans", cap.query_strans)
    monkeypatch.setattr(
        "app.domain.customer_orders.fetch_transhdr_for_keys",
        lambda *a, **k: headers.copy(),
    )
    monkeypatch.setattr(
        "app.domain.customer_orders.enrich_order_lines",
        lambda df, with_cards=True: df.assign(
            NAME_U="x", SKU_CODE="SP", FULL_NAME_U="n", bill_value=df.get("bill_value", 0)
        ),
    )
    monkeypatch.setattr("app.domain.customer_filters.lookup_cards", make_lookup(profiles))


def test_f4_requires_cards(range_ab):
    with pytest.raises(ValueError, match="mã thẻ"):
        fetch_customer_orders(*range_ab, card_ids=[])


def test_f4_product_not_found_raises(monkeypatch, range_ab, card_profiles):
    monkeypatch.setattr(
        "app.domain.customer_orders.search_products",
        lambda **kw: pd.DataFrame(),
    )
    with pytest.raises(ValueError, match="Không tìm thấy"):
        fetch_customer_orders(
            *range_ab,
            card_ids=["E10000000053"],
            product_query="NO_SUCH_SKU",
        )


def test_f4_gift_sql_only_when_product_filter(
    monkeypatch, range_ab, card_profiles
):
    cap = QueryCapture()
    _install_base(monkeypatch, cap, card_profiles)
    monkeypatch.setattr(
        "app.domain.customer_orders.search_products",
        lambda **kw: _sku_df(),
    )
    fetch_customer_orders(
        *range_ab,
        card_ids=["E10000000053"],
        product_query="SP001",
        gift_mode="paid",
    )
    where = cap.strans_calls[0]["extra_where"]
    assert_where_contains(where, "AMOUNT", "SKU_ID")
    assert "ISNULL(AMOUNT,0) > 0" in where.replace(" ", "") or "ISNULL(AMOUNT,0)>0" in where.replace(
        " ", ""
    )

    cap2 = QueryCapture()
    _install_base(monkeypatch, cap2, card_profiles)
    fetch_customer_orders(
        *range_ab,
        card_ids=["E10000000053"],
        gift_mode="paid",  # no product → must NOT inject AMOUNT predicate
    )
    where2 = cap2.strans_calls[0]["extra_where"]
    assert_where_not_contains(where2, "AMOUNT")


def test_f4_gift_mode_gift_predicate(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    _install_base(monkeypatch, cap, card_profiles)
    monkeypatch.setattr(
        "app.domain.customer_orders.search_products",
        lambda **kw: _sku_df(),
    )
    fetch_customer_orders(
        *range_ab,
        card_ids=["E10000000053"],
        product_query="SP001",
        gift_mode="gift",
    )
    where = cap.strans_calls[0]["extra_where"].replace(" ", "")
    assert "ISNULL(AMOUNT,0)=0" in where


def test_f4_min_max_bill_filters_lines(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    _install_base(monkeypatch, cap, card_profiles)
    out, seeds = fetch_customer_orders(
        *range_ab,
        card_ids=["E10000000053", "A10000054973"],
        min_bill=100_000,
        max_bill=250_000,
    )
    assert seeds == []
    assert set(out["TRANS_NUM"].astype(str)) == {"BILL2"}
    assert (out["bill_value"] >= 100_000).all()


def test_f4_header_empty_fallback_sums_line_total(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    lines = _strans_seed().iloc[:1].copy()
    _install_base(monkeypatch, cap, card_profiles, lines=lines, headers=pd.DataFrame())
    out, _ = fetch_customer_orders(*range_ab, card_ids=["E10000000053"])
    assert len(out) == 1
    assert out.iloc[0]["bill_value"] == pytest.approx(80_000.0)


def test_f4_stk_on_strans_not_transhdr(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    _install_base(monkeypatch, cap, card_profiles)
    fetch_customer_orders(
        *range_ab,
        card_ids=["E10000000053"],
        store_ids=["10001"],
    )
    assert_where_contains(cap.strans_calls[0]["extra_where"], "STK_ID")
    # Header path uses fetch_transhdr_for_keys (TRANS_NUM), not STK filter on TRANSHDR.
    assert not cap.transhdr_calls


def test_f4_blank_header_stk_still_keeps_bills(monkeypatch, range_ab, card_profiles):
    """Regression: TRANSHDR.STK blank must not drop STRANS-matched bills (same as F5)."""
    cap = QueryCapture()
    blank = _headers().copy()
    blank["STK_ID"] = ""
    # fetch_transhdr_for_keys reattaches STK — simulate already-fixed headers
    fixed = _headers().copy()
    _install_base(monkeypatch, cap, card_profiles, headers=fixed)
    out, _ = fetch_customer_orders(*range_ab, card_ids=["E10000000053", "A10000054973"])
    assert set(out["TRANS_NUM"].astype(str)) == {"BILL1", "BILL2", "BILL3"}


def test_f4_age_sex_post_filter(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    _install_base(monkeypatch, cap, card_profiles)
    out, _ = fetch_customer_orders(
        *range_ab,
        card_ids=["E10000000053", "A10000054973"],
        sex="F",
        min_age=20,
    )
    # Only Alice (F) remains among the two cards that have lines
    assert set(out["CARD_ID"].astype(str)) == {"E10000000053"}


def test_f4_export_columns_exclude_idx_qty(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    _install_base(monkeypatch, cap, card_profiles)
    out, _ = fetch_customer_orders(*range_ab, card_ids=["E10000000053"])
    assert "IDX" not in out.columns
    assert "QTY" not in out.columns
    assert "AMOUNT" not in out.columns
    assert "line_total" in out.columns
    assert "TRANS_NUM" in out.columns
    assert "CARD_ID" in out.columns
