"""F5 product orders — seed gift/paid, TRANSHDR rematch, customer filters, tokens."""
from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from app.domain.columns import ORDER_COLUMNS
from app.domain.product_orders import fetch_product_orders, _orders_for_skus
from tests.conftest import QueryCapture, assert_where_contains, make_lookup


def _seed_lines() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "STK_ID": "10001",
                "TRANS_NUM": "P1",
                "TRAN_DATE": date(2026, 7, 1),
                "TRAN_TIME": "09:00",
                "CARD_ID": "E10000000053",
                "TRANS_CODE": "113",
                "line_total": 30_000.0,
            },
            {
                "STK_ID": "10001",
                "TRANS_NUM": "P2",
                "TRAN_DATE": date(2026, 7, 2),
                "TRAN_TIME": "10:00",
                "CARD_ID": "A10000054973",
                "TRANS_CODE": "113",
                "line_total": 500_000.0,
            },
            {
                "STK_ID": "10004",
                "TRANS_NUM": "P3",
                "TRAN_DATE": date(2026, 7, 3),
                "TRAN_TIME": "11:00",
                "CARD_ID": "E10000000099",
                "TRANS_CODE": "113",
                "line_total": 40_000.0,
            },
        ]
    )


def _hdr_blank_stk() -> pd.DataFrame:
    """Simulate live TRANSHDR with blank STK_ID — F5 must reattach from STRANS keys."""
    return pd.DataFrame(
        [
            {
                "STK_ID": "",
                "TRANS_NUM": "P1",
                "TRAN_DATE": date(2026, 7, 1),
                "TRAN_TIME": "09:00",
                "CARD_ID": "E10000000053",
                "TRANS_CODE": "113",
                "bill_value": 90_000.0,
            },
            {
                "STK_ID": "",
                "TRANS_NUM": "P2",
                "TRAN_DATE": date(2026, 7, 2),
                "TRAN_TIME": "10:00",
                "CARD_ID": "A10000054973",
                "TRANS_CODE": "113",
                "bill_value": 500_000.0,
            },
            {
                "STK_ID": "",
                "TRANS_NUM": "P3",
                "TRAN_DATE": date(2026, 7, 3),
                "TRAN_TIME": "11:00",
                "CARD_ID": "E10000000099",
                "TRANS_CODE": "113",
                "bill_value": 120_000.0,
            },
        ]
    )


def _install_orders(monkeypatch, cap: QueryCapture, profiles, *, lines=None, use_real_transhdr=True):
    lines = _seed_lines() if lines is None else lines
    cap.set_strans(lambda *a, **k: lines.copy())
    monkeypatch.setattr("app.domain.product_orders.query_strans", cap.query_strans)

    if use_real_transhdr:
        # Drive fetch_transhdr_for_keys via query_transhdr stub + real merge logic
        from app.domain import bill_expand as be

        hdr = _hdr_blank_stk()

        def fake_transhdr(date_start, date_end, body, *, extra_where="", extra_params=None, progress=None):
            # Return all headers; merge logic filters by TRANS_NUM
            nums = set(str(x).strip() for x in (extra_params or []))
            part = hdr.copy()
            if nums:
                part = part.loc[part["TRANS_NUM"].astype(str).isin(nums)]
            return part

        monkeypatch.setattr(be, "query_transhdr", fake_transhdr)
        # product_orders imports fetch_transhdr_for_keys by name — keep real
    else:
        monkeypatch.setattr(
            "app.domain.product_orders.fetch_transhdr_for_keys",
            lambda *a, **k: pd.DataFrame(),
        )

    monkeypatch.setattr(
        "app.domain.product_orders.lookup_cards",
        make_lookup(profiles),
    )
    monkeypatch.setattr(
        "app.domain.customer_filters.lookup_cards",
        make_lookup(profiles),
    )


def test_f5_gift_paid_always_on_seed_sql(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    _install_orders(monkeypatch, cap, card_profiles)
    _orders_for_skus(
        *range_ab,
        ["1001"],
        store_ids=None,
        require_card=True,
        min_bill=None,
        max_bill=None,
        gift_mode="paid",
        progress=None,
    )
    where = cap.strans_calls[0]["extra_where"].replace(" ", "")
    assert "ISNULL(AMOUNT,0)>0" in where


def test_f5_customer_filters_force_require_card(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    _install_orders(monkeypatch, cap, card_profiles)
    _orders_for_skus(
        *range_ab,
        ["1001"],
        store_ids=None,
        require_card=False,  # caller said no — but age filter must force card
        min_bill=None,
        max_bill=None,
        gift_mode="any",
        progress=None,
        min_age=20,
    )
    where = cap.strans_calls[0]["extra_where"]
    assert_where_contains(where, "CARD_ID IS NOT NULL")


def test_f5_reattach_stk_from_strans_keys(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    _install_orders(monkeypatch, cap, card_profiles, use_real_transhdr=True)
    out = _orders_for_skus(
        *range_ab,
        ["1001"],
        store_ids=None,
        require_card=True,
        min_bill=None,
        max_bill=None,
        gift_mode="any",
        progress=None,
    )
    assert not out.empty
    # STK must come from STRANS keys, not blank header
    assert set(out["STK_ID"].astype(str)) <= {"10001", "10004"}
    assert (out["STK_ID"].astype(str).str.strip() != "").all()
    assert out.iloc[0]["bill_value"] > 0


def test_f5_header_fallback_sums_seed_lines(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    _install_orders(monkeypatch, cap, card_profiles, use_real_transhdr=False)
    out = _orders_for_skus(
        *range_ab,
        ["1001"],
        store_ids=None,
        require_card=True,
        min_bill=None,
        max_bill=None,
        gift_mode="any",
        progress=None,
    )
    by = out.set_index("TRANS_NUM")
    assert by.loc["P1", "bill_value"] == pytest.approx(30_000.0)
    assert by.loc["P2", "bill_value"] == pytest.approx(500_000.0)


def test_f5_min_max_bill(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    _install_orders(monkeypatch, cap, card_profiles, use_real_transhdr=False)
    out = _orders_for_skus(
        *range_ab,
        ["1001"],
        store_ids=None,
        require_card=True,
        min_bill=100_000,
        max_bill=600_000,
        gift_mode="any",
        progress=None,
    )
    assert set(out["TRANS_NUM"].astype(str)) == {"P2"}


def test_f5_birth_month_sex_filter(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    _install_orders(monkeypatch, cap, card_profiles, use_real_transhdr=False)
    out = _orders_for_skus(
        *range_ab,
        ["1001"],
        store_ids=None,
        require_card=True,
        min_bill=None,
        max_bill=None,
        gift_mode="any",
        progress=None,
        birth_month=7,
        sex="F",
    )
    # Alice (P1) + Carol (P3)
    assert set(out["CARD_ID"].astype(str)) == {"E10000000053", "E10000000099"}


def test_f5_prefix_in_sql(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    _install_orders(monkeypatch, cap, card_profiles, use_real_transhdr=False)
    _orders_for_skus(
        *range_ab,
        ["1001"],
        store_ids=["10001"],
        require_card=True,
        min_bill=None,
        max_bill=None,
        gift_mode="any",
        progress=None,
        card_prefix="E",
    )
    where = cap.strans_calls[0]["extra_where"]
    assert_where_contains(where, "CARD_ID", "STK_ID")
    assert any(str(p).startswith("E") or "%" in str(p) for p in cap.strans_calls[0]["extra_params"])


def test_f5_fetch_unresolved_tokens(monkeypatch, range_ab, card_profiles):
    monkeypatch.setattr(
        "app.domain.product_orders.resolve_product_tokens",
        lambda tokens, **kw: {t: pd.DataFrame() for t in tokens},
    )
    per, unresolved, seeds = fetch_product_orders(
        *range_ab, ["NOPE"], require_card=True
    )
    assert unresolved == ["NOPE"]
    assert per["NOPE"].empty
    assert seeds["NOPE"] == []


def test_f5_fetch_multi_token_isolation(monkeypatch, range_ab, card_profiles):
    sku_map = {
        "SP001": pd.DataFrame([{"SKU_ID": "1001"}]),
        "SP002": pd.DataFrame([{"SKU_ID": "1002"}]),
    }
    monkeypatch.setattr(
        "app.domain.product_orders.resolve_product_tokens",
        lambda tokens, **kw: {t: sku_map[t].copy() for t in tokens},
    )

    calls = {"skus": []}

    def fake_orders(date_start, date_end, sku_ids, **kwargs):
        calls["skus"].append(list(sku_ids))
        return pd.DataFrame(
            [
                {
                    "TRANS_NUM": f"T-{sku_ids[0]}",
                    "STK_ID": "10001",
                    "TRAN_DATE": date(2026, 7, 1),
                    "TRAN_TIME": "1",
                    "CARD_ID": "E10000000053",
                    "NAME_U": "Alice",
                    "TRANS_CODE": "113",
                    "bill_value": 1.0,
                }
            ]
        )

    monkeypatch.setattr("app.domain.product_orders._orders_for_skus", fake_orders)
    per, unresolved, seeds = fetch_product_orders(
        *range_ab, ["SP001", "SP002"], require_card=True
    )
    assert unresolved == []
    assert seeds["SP001"] == ["1001"]
    assert seeds["SP002"] == ["1002"]
    assert calls["skus"] == [["1001"], ["1002"]]
    assert set(per.keys()) == {"SP001", "SP002"}
    for col in ORDER_COLUMNS:
        assert col in per["SP001"].columns
