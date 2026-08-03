"""Deep unit tests for CSCARD attribute filters."""
from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from app.domain.customer_filters import customer_filters_active, filter_frame_by_customer
from app.domain.search_opts import SearchOpts
from app.export.txt_report import age_years


def test_filters_active_matrix():
    assert not customer_filters_active()
    assert customer_filters_active(min_age=30)
    assert customer_filters_active(max_age=50)
    assert customer_filters_active(sex="M")
    assert not customer_filters_active(sex="any")
    assert customer_filters_active(card_prefix="E")
    assert customer_filters_active(birth_month=7)
    assert not customer_filters_active(birth_month=None)


def test_filter_by_prefix_only_no_lookup(monkeypatch, card_profiles):
    called = {"n": 0}

    def boom(_):
        called["n"] += 1
        raise AssertionError("lookup_cards must not run for prefix-only")

    monkeypatch.setattr("app.domain.customer_filters.lookup_cards", boom)
    df = pd.DataFrame(
        {
            "CARD_ID": ["E10000000053", "A10000054973", "", "nan"],
            "SKU_ID": ["1", "2", "3", "4"],
        }
    )
    out = filter_frame_by_customer(df, card_prefix="E")
    assert list(out["CARD_ID"]) == ["E10000000053"]
    assert called["n"] == 0


def test_filter_prefix_case_sensitive(monkeypatch):
    monkeypatch.setattr(
        "app.domain.customer_filters.lookup_cards",
        lambda ids: pd.DataFrame(),
    )
    df = pd.DataFrame({"CARD_ID": ["E100", "e100", "A100"]})
    out = filter_frame_by_customer(
        df, card_prefix="E", search=SearchOpts(case_insensitive=False, fuzzy=False)
    )
    assert list(out["CARD_ID"]) == ["E100"]


def test_filter_sex_aliases(monkeypatch, card_profiles):
    monkeypatch.setattr(
        "app.domain.customer_filters.lookup_cards",
        lambda ids: card_profiles.loc[card_profiles["CARD_ID"].isin(ids)].copy(),
    )
    df = pd.DataFrame({"CARD_ID": card_profiles["CARD_ID"].tolist()})
    out_m = filter_frame_by_customer(df, sex="M")
    # Bob (M) + Dan (SEX=1 → M)
    assert set(out_m["CARD_ID"]) == {"A10000054973", "B10000000001"}
    out_f = filter_frame_by_customer(df, sex="F")
    assert set(out_f["CARD_ID"]) == {"E10000000053", "E10000000099"}


def test_filter_age_as_of_boundary(monkeypatch, card_profiles):
    monkeypatch.setattr(
        "app.domain.customer_filters.lookup_cards",
        lambda ids: card_profiles.loc[card_profiles["CARD_ID"].isin(ids)].copy(),
    )
    df = pd.DataFrame({"CARD_ID": card_profiles["CARD_ID"].tolist()})
    as_of = date(2026, 7, 27)
    # days/365.25 ages: Alice~36.03, Bob~41.5, Carol~31.07, Dan~25.56
    out = filter_frame_by_customer(df, min_age=30, max_age=37, as_of=as_of)
    assert set(out["CARD_ID"]) == {"E10000000053", "E10000000099"}


def test_filter_birth_month(monkeypatch, card_profiles):
    monkeypatch.setattr(
        "app.domain.customer_filters.lookup_cards",
        lambda ids: card_profiles.loc[card_profiles["CARD_ID"].isin(ids)].copy(),
    )
    df = pd.DataFrame({"CARD_ID": card_profiles["CARD_ID"].tolist()})
    out = filter_frame_by_customer(df, birth_month=7)
    assert set(out["CARD_ID"]) == {"E10000000053", "E10000000099"}


def test_filter_birth_month_invalid_raises(monkeypatch, card_profiles):
    monkeypatch.setattr(
        "app.domain.customer_filters.lookup_cards",
        lambda ids: card_profiles.copy(),
    )
    df = pd.DataFrame({"CARD_ID": ["E10000000053"]})
    with pytest.raises(ValueError, match="1–12"):
        filter_frame_by_customer(df, birth_month=13)


def test_filter_combined_prefix_age_sex_month(monkeypatch, card_profiles):
    monkeypatch.setattr(
        "app.domain.customer_filters.lookup_cards",
        lambda ids: card_profiles.loc[card_profiles["CARD_ID"].isin(ids)].copy(),
    )
    df = pd.DataFrame({"CARD_ID": card_profiles["CARD_ID"].tolist(), "v": [1, 2, 3, 4]})
    # E* → Alice+Carol; F + month 7 + age<=35 → Carol only (~31)
    out = filter_frame_by_customer(
        df,
        card_prefix="E",
        sex="F",
        birth_month=7,
        max_age=35,
        as_of=date(2026, 7, 27),
    )
    assert list(out["CARD_ID"]) == ["E10000000099"]


def test_filter_empty_lookup_returns_empty(monkeypatch):
    monkeypatch.setattr(
        "app.domain.customer_filters.lookup_cards",
        lambda ids: pd.DataFrame(),
    )
    df = pd.DataFrame({"CARD_ID": ["X1"]})
    out = filter_frame_by_customer(df, min_age=20)
    assert out.empty


def test_filter_missing_card_column_when_active():
    df = pd.DataFrame({"SKU_ID": ["1"]})
    out = filter_frame_by_customer(df, sex="M")
    assert out.empty


def test_filter_inactive_is_identity():
    df = pd.DataFrame({"CARD_ID": ["A", "B"], "x": [1, 2]})
    out = filter_frame_by_customer(df)
    assert list(out["CARD_ID"]) == ["A", "B"]


def test_age_years_basic():
    from datetime import datetime

    assert age_years("1990-01-01", as_of=datetime(2026, 7, 27)) is not None
    assert age_years("1990-01-01", as_of=datetime(2026, 7, 27)) == pytest.approx(36.55, abs=0.1)
    assert age_years(None) is None
