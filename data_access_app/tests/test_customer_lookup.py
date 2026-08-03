"""F2 customer search + lookup_cards chunking."""
from __future__ import annotations

import pandas as pd
import pytest

from app.domain.columns import CARD_LOOKUP_COLUMNS, CUSTOMER_COLUMNS
from app.domain.customer import lookup_cards, search_customers


def test_search_customers_requires_clause():
    with pytest.raises(ValueError):
        search_customers()


def test_search_customers_birth_month_sql(monkeypatch):
    seen = {}

    def fake_master(sql, params=None):
        seen["sql"] = sql
        seen["params"] = list(params or [])
        return pd.DataFrame(
            [
                {
                    "CARD_ID": "E1",
                    "NAME_U": "Alice",
                    "NAME": "",
                    "PHONE": "1",
                    "SEX": "F",
                    "BIRTHDAY": "1990-07-01",
                    "CUST_ID": "c1",
                }
            ]
        )

    monkeypatch.setattr("app.domain.customer.master_select", fake_master)
    out = search_customers(birth_month=7)
    assert "MONTH(BIRTHDAY)" in seen["sql"].replace(" ", "")
    assert 7 in seen["params"]
    assert list(out.columns) == CUSTOMER_COLUMNS
    assert out.iloc[0]["NAME"] == "Alice"  # NAME_U preferred into NAME


def test_search_customers_invalid_birth_month():
    with pytest.raises(ValueError, match="1–12"):
        search_customers(birth_month=0)


def test_lookup_cards_chunks_400(monkeypatch):
    calls = []

    def fake_master(sql, params=None):
        calls.append(list(params or []))
        return pd.DataFrame(
            [
                {
                    "CARD_ID": p,
                    "NAME_U": "n",
                    "NAME": "n",
                    "PHONE": "",
                    "MOBI": "",
                    "SEX": "M",
                    "BIRTHDAY": None,
                    "DISC_LVL": "1",
                    "CUST_ID": "c",
                }
                for p in (params or [])
            ]
        )

    monkeypatch.setattr("app.domain.customer.master_select", fake_master)
    ids = [f"C{i:04d}" for i in range(850)]
    out = lookup_cards(ids)
    assert len(calls) == 3  # 400 + 400 + 50
    assert len(calls[0]) == 400
    assert len(calls[1]) == 400
    assert len(calls[2]) == 50
    assert len(out) == 850
    for c in CARD_LOOKUP_COLUMNS:
        assert c in out.columns


def test_lookup_cards_empty():
    assert lookup_cards([]).empty
    assert lookup_cards(["", "  "]).empty
