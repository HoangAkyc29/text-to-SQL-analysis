"""bill_expand — keys, TRANSHDR rematch, full-bill expand, cohort lines."""
from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from app.domain.bill_expand import (
    bill_keys_from_lines,
    enrich_order_lines,
    fetch_bill_lines,
    fetch_card_period_lines,
    fetch_transhdr_for_keys,
)
from app.domain.columns import ORDER_COLUMNS, ORDER_LINE_COLUMNS
from tests.conftest import QueryCapture, make_lookup


def test_bill_keys_dedupe_and_strip():
    df = pd.DataFrame(
        {
            "STK_ID": [" 10001 ", "10001", "10004", None],
            "TRANS_NUM": [" T1 ", "T1", "T2", "T3"],
            "x": [1, 2, 3, 4],
        }
    )
    keys = bill_keys_from_lines(df)
    assert list(keys.columns) == ["STK_ID", "TRANS_NUM"]
    assert len(keys) == 2
    assert set(map(tuple, keys.values.tolist())) == {("10001", "T1"), ("10004", "T2")}


def test_bill_keys_empty():
    assert bill_keys_from_lines(pd.DataFrame()).empty
    assert bill_keys_from_lines(None).empty


def test_fetch_transhdr_reattaches_stk(monkeypatch, range_ab):
    hdr_rows = pd.DataFrame(
        [
            {
                "STK_ID": "",
                "TRANS_NUM": "T1",
                "TRAN_DATE": date(2026, 7, 1),
                "TRAN_TIME": "10",
                "CARD_ID": "E1",
                "TRANS_CODE": "113",
                "bill_value": 100.0,
            },
            {
                "STK_ID": "",
                "TRANS_NUM": "T2",
                "TRAN_DATE": date(2026, 7, 2),
                "TRAN_TIME": "11",
                "CARD_ID": "E2",
                "TRANS_CODE": "113",
                "bill_value": 200.0,
            },
        ]
    )

    def fake_transhdr(*a, extra_where="", extra_params=None, **k):
        nums = {str(x).strip() for x in (extra_params or [])}
        return hdr_rows.loc[hdr_rows["TRANS_NUM"].isin(nums)].copy()

    monkeypatch.setattr("app.domain.bill_expand.query_transhdr", fake_transhdr)
    keys = pd.DataFrame(
        {
            "STK_ID": ["10001", "10004"],
            "TRANS_NUM": ["T1", "T2"],
            "TRANS_CODE": ["113", "113"],
        }
    )
    out = fetch_transhdr_for_keys(*range_ab, keys)
    assert not out.empty
    by = out.set_index("TRANS_NUM")
    assert by.loc["T1", "STK_ID"] == "10001"
    assert by.loc["T2", "STK_ID"] == "10004"
    assert by.loc["T1", "bill_value"] == pytest.approx(100.0)
    for c in ORDER_COLUMNS:
        if c != "NAME_U":
            assert c in out.columns or c == "NAME_U"


def test_fetch_transhdr_empty_keys(range_ab):
    out = fetch_transhdr_for_keys(*range_ab, pd.DataFrame(columns=["STK_ID", "TRANS_NUM"]))
    assert out.empty


def test_enrich_order_lines_sku_and_card(monkeypatch, card_profiles):
    monkeypatch.setattr(
        "app.domain.bill_expand.master_select",
        lambda sql, params=None: pd.DataFrame(
            [{"SKU_ID": "1001", "SKU_CODE": "SP001", "FULL_NAME_U": "Sữa tươi"}]
        ),
    )
    monkeypatch.setattr("app.domain.bill_expand.lookup_cards", make_lookup(card_profiles))
    raw = pd.DataFrame(
        [
            {
                "STK_ID": "10001",
                "TRANS_NUM": "T1",
                "TRAN_DATE": date(2026, 7, 1),
                "TRAN_TIME": "10",
                "CARD_ID": "E10000000053",
                "TRANS_CODE": "113",
                "IDX": 1,
                "SKU_ID": "1001",
                "QTY": 2,
                "UNIT_SYMB": "HOP",
                "line_total": 60_000.0,
            }
        ]
    )
    out = enrich_order_lines(raw)
    assert out.iloc[0]["SKU_CODE"] == "SP001"
    assert out.iloc[0]["FULL_NAME_U"] == "Sữa tươi"
    assert out.iloc[0]["NAME_U"] == "Alice"
    assert "AMOUNT" not in out.columns
    assert "line_total" in out.columns
    for c in ("TRANS_NUM", "STK_ID", "SKU_ID", "SKU_CODE", "FULL_NAME_U", "NAME_U", "line_total"):
        assert c in out.columns


def test_fetch_bill_lines_chunks_or_clauses(monkeypatch, range_ab):
    cap = QueryCapture()
    calls_params = []

    def fake_strans(*a, extra_where="", extra_params=None, **k):
        calls_params.append(list(extra_params or []))
        # one line per requested key pair
        rows = []
        params = list(extra_params or [])
        for i in range(0, len(params), 2):
            rows.append(
                {
                    "STK_ID": params[i],
                    "TRANS_NUM": params[i + 1],
                    "TRAN_DATE": date(2026, 7, 1),
                    "TRAN_TIME": "10",
                    "CARD_ID": "E1",
                    "TRANS_CODE": "113",
                    "IDX": 1,
                    "SKU_ID": "1001",
                    "QTY": 1,
                    "UNIT_SYMB": "HOP",
                    "line_total": 10.0,
                }
            )
        return pd.DataFrame(rows)

    monkeypatch.setattr("app.domain.bill_expand.query_strans", fake_strans)
    monkeypatch.setattr(
        "app.domain.bill_expand.enrich_order_lines",
        lambda df, with_cards=True: df,
    )
    keys = pd.DataFrame(
        {
            "STK_ID": [f"S{i}" for i in range(45)],
            "TRANS_NUM": [f"T{i}" for i in range(45)],
        }
    )
    out = fetch_bill_lines(*range_ab, keys)
    # chunk size 40 → 2 calls
    assert len(calls_params) == 2
    assert len(calls_params[0]) == 80  # 40 pairs × 2
    assert len(calls_params[1]) == 10  # 5 pairs × 2
    assert len(out) == 45


def test_fetch_card_period_lines_store_filter(monkeypatch, range_ab):
    seen = {}

    def fake_strans(*a, extra_where="", extra_params=None, **k):
        seen["where"] = extra_where
        seen["params"] = list(extra_params or [])
        return pd.DataFrame(
            [
                {
                    "STK_ID": "10001",
                    "TRANS_NUM": "T1",
                    "TRAN_DATE": date(2026, 7, 1),
                    "TRAN_TIME": "10",
                    "CARD_ID": "E1",
                    "TRANS_CODE": "113",
                    "IDX": 1,
                    "SKU_ID": "1001",
                    "QTY": 1,
                    "UNIT_SYMB": "HOP",
                    "line_total": 5.0,
                }
            ]
        )

    monkeypatch.setattr("app.domain.bill_expand.query_strans", fake_strans)
    monkeypatch.setattr(
        "app.domain.bill_expand.enrich_order_lines",
        lambda df, with_cards=True: df,
    )
    out = fetch_card_period_lines(
        *range_ab, ["E1", "E2"], store_ids=["10001", "10004"]
    )
    assert "STK_ID" in seen["where"]
    assert "10001" in seen["params"] and "10004" in seen["params"]
    assert "E1" in seen["params"]
    assert len(out) == 1


def test_fetch_card_period_lines_empty_cards(range_ab):
    assert fetch_card_period_lines(*range_ab, []).empty
