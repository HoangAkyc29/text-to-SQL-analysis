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


def test_f5_fetch_empty_tokens_means_all_products(monkeypatch, range_ab, card_profiles):
    from app.domain.product_orders import ALL_PRODUCTS_LABEL

    calls = {"skus": None}

    def fake_orders(date_start, date_end, sku_ids, **kwargs):
        calls["skus"] = list(sku_ids)
        return pd.DataFrame(
            [
                {
                    "TRANS_NUM": "P-ALL",
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
    resolve_calls = {"n": 0}

    def fake_resolve(tokens, **kw):
        resolve_calls["n"] += 1
        return {}

    monkeypatch.setattr("app.domain.product_orders.resolve_product_tokens", fake_resolve)

    per, unresolved, seeds = fetch_product_orders(*range_ab, [], require_card=True)
    assert resolve_calls["n"] == 0
    assert calls["skus"] == []
    assert unresolved == []
    assert set(per.keys()) == {ALL_PRODUCTS_LABEL}
    assert seeds[ALL_PRODUCTS_LABEL] == []
    assert len(per[ALL_PRODUCTS_LABEL]) == 1

    per2, _, _ = fetch_product_orders(*range_ab, ["  ", ""], require_card=True)
    assert set(per2.keys()) == {ALL_PRODUCTS_LABEL}


def test_f5_orders_all_products_uses_distinct_strans_then_hdr(
    monkeypatch, range_ab, card_profiles
):
    """Empty SKU → DISTINCT STRANS keys (STK from lines) + TRANSHDR bill_value."""
    cap = QueryCapture()
    _install_orders(monkeypatch, cap, card_profiles, use_real_transhdr=True)
    out = _orders_for_skus(
        *range_ab,
        [],
        store_ids=None,
        require_card=True,
        min_bill=None,
        max_bill=None,
        gift_mode="any",
        progress=None,
    )
    assert cap.strans_calls
    body = cap.strans_calls[0]["body"].upper()
    assert "DISTINCT" in body
    assert "SKU_ID" not in (cap.strans_calls[0]["extra_where"] or "")
    assert not out.empty
    # STK must come from STRANS keys, not blank HDR
    assert (out["STK_ID"].astype(str).str.strip() != "").all()
    assert set(out["STK_ID"].astype(str)) <= {"10001", "10004"}


def test_f5_orders_all_with_store_uses_distinct_strans(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    _install_orders(monkeypatch, cap, card_profiles)
    _orders_for_skus(
        *range_ab,
        [],
        store_ids=["10001"],
        require_card=True,
        min_bill=None,
        max_bill=None,
        gift_mode="any",
        progress=None,
    )
    assert cap.strans_calls
    body = cap.strans_calls[0]["body"].upper()
    assert "DISTINCT" in body
    assert "SKU_ID" not in (cap.strans_calls[0]["extra_where"] or "")
    assert "10001" in cap.strans_calls[0]["extra_params"]


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

    seed_calls: list[list[str]] = []

    def fake_seed(date_start, date_end, sku_ids, **kwargs):
        seed_calls.append(list(sku_ids))
        return pd.DataFrame(
            [
                {
                    "STK_ID": "10001",
                    "TRANS_NUM": "T-1001",
                    "TRAN_DATE": date(2026, 7, 1),
                    "TRAN_TIME": "1",
                    "CARD_ID": "E10000000053",
                    "TRANS_CODE": "113",
                    "SKU_ID": "1001",
                    "line_total": 1.0,
                },
                {
                    "STK_ID": "10001",
                    "TRANS_NUM": "T-1002",
                    "TRAN_DATE": date(2026, 7, 1),
                    "TRAN_TIME": "2",
                    "CARD_ID": "E10000000053",
                    "TRANS_CODE": "113",
                    "SKU_ID": "1002",
                    "line_total": 2.0,
                },
            ]
        )

    def fake_hdr(date_start, date_end, bill_keys, **kwargs):
        return pd.DataFrame(
            [
                {
                    "STK_ID": "10001",
                    "TRANS_NUM": "T-1001",
                    "TRAN_DATE": date(2026, 7, 1),
                    "TRAN_TIME": "1",
                    "CARD_ID": "E10000000053",
                    "TRANS_CODE": "113",
                    "bill_value": 10.0,
                },
                {
                    "STK_ID": "10001",
                    "TRANS_NUM": "T-1002",
                    "TRAN_DATE": date(2026, 7, 1),
                    "TRAN_TIME": "2",
                    "CARD_ID": "E10000000053",
                    "TRANS_CODE": "113",
                    "bill_value": 20.0,
                },
            ]
        )

    monkeypatch.setattr("app.domain.product_orders._seed_lines_for_skus", fake_seed)
    monkeypatch.setattr("app.domain.product_orders.fetch_transhdr_for_keys", fake_hdr)
    monkeypatch.setattr(
        "app.domain.product_orders.lookup_cards", make_lookup(card_profiles)
    )
    per, unresolved, seeds = fetch_product_orders(
        *range_ab, ["SP001", "SP002"], require_card=True
    )
    assert unresolved == []
    assert seeds["SP001"] == ["1001"]
    assert seeds["SP002"] == ["1002"]
    # One shared STRANS seed pull with both SKUs
    assert len(seed_calls) == 1
    assert set(seed_calls[0]) == {"1001", "1002"}
    assert set(per.keys()) == {"SP001", "SP002"}
    assert set(per["SP001"]["TRANS_NUM"].astype(str)) == {"T-1001"}
    assert set(per["SP002"]["TRANS_NUM"].astype(str)) == {"T-1002"}
    for col in ORDER_COLUMNS:
        assert col in per["SP001"].columns
