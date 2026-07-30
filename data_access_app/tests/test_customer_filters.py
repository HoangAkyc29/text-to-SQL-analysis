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


def test_filter_by_prefix_only():
    df = pd.DataFrame(
        {
            "CARD_ID": ["E10000000053", "A10000054973", ""],
            "SKU_ID": ["1", "2", "3"],
        }
    )
    out = filter_frame_by_customer(df, card_prefix="E")
    assert list(out["CARD_ID"]) == ["E10000000053"]


def test_age_years_basic():
    assert age_years("1990-01-01") is not None
    assert age_years(None) is None
