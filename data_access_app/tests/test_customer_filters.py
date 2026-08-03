"""Tests for customer attribute filters."""
from __future__ import annotations

import pandas as pd

from app.domain.customer_filters import customer_filters_active, filter_frame_by_customer
from app.export.txt_report import age_years


def test_filters_active():
    assert not customer_filters_active()
    assert customer_filters_active(min_age=30)
    assert customer_filters_active(sex="M")
    assert customer_filters_active(card_prefix="E")
    assert customer_filters_active(birth_month=7)


def test_filter_by_prefix_only():
    df = pd.DataFrame(
        {
            "CARD_ID": ["E10000000053", "A10000054973", ""],
            "SKU_ID": ["1", "2", "3"],
        }
    )
    out = filter_frame_by_customer(df, card_prefix="E")
    assert list(out["CARD_ID"]) == ["E10000000053"]


def test_filter_by_birth_month(monkeypatch):
    df = pd.DataFrame({"CARD_ID": ["C1", "C2", "C3"], "x": [1, 2, 3]})
    cards = pd.DataFrame(
        {
            "CARD_ID": ["C1", "C2", "C3"],
            "BIRTHDAY": ["1990-07-15", "1988-01-01", "1995-07-20"],
            "SEX": ["M", "F", "F"],
        }
    )

    def _fake_lookup(ids):
        return cards.loc[cards["CARD_ID"].isin(ids)].copy()

    monkeypatch.setattr("app.domain.customer_filters.lookup_cards", _fake_lookup)
    out = filter_frame_by_customer(df, birth_month=7)
    assert sorted(out["CARD_ID"].tolist()) == ["C1", "C3"]


def test_age_years_basic():
    assert age_years("1990-01-01") is not None
    assert age_years(None) is None
