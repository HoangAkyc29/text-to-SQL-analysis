"""F3 loyalty fetch — aggregation, metric filters, STK, customer filters."""
from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from app.domain.columns import LOYALTY_METRIC_COLUMNS, POINTS_DIVISOR
from app.domain.loyalty_customers import fetch_loyalty_customers
from tests.conftest import QueryCapture, assert_where_contains, make_lookup, points_of


@pytest.fixture
def loyalty_agg() -> pd.DataFrame:
    """Shape returned by SQL GROUP BY (per shard / target)."""
    # Alice: 150_000 → 3 points, 2 bills
    # Bob: 600_000 → 12 points, 1 bill
    # Carol: 50_000 → 1 point, 1 bill (store 10004)
    return pd.DataFrame(
        [
            {
                "CARD_ID": "E10000000053",
                "STK_ID": "10001",
                "total_value": 150_000.0,
                "bill_count": 2,
            },
            {
                "CARD_ID": "A10000054973",
                "STK_ID": "10001",
                "total_value": 600_000.0,
                "bill_count": 1,
            },
            {
                "CARD_ID": "E10000000099",
                "STK_ID": "10004",
                "total_value": 50_000.0,
                "bill_count": 1,
            },
        ]
    )


def _install(monkeypatch, cap: QueryCapture, lines: pd.DataFrame, profiles: pd.DataFrame):
    cap.set_strans(lambda *a, **k: lines.copy())
    monkeypatch.setattr("app.domain.loyalty_customers.query_strans", cap.query_strans)
    monkeypatch.setattr("app.domain.loyalty_customers.lookup_cards", make_lookup(profiles))
    monkeypatch.setattr("app.domain.customer_filters.lookup_cards", make_lookup(profiles))


def test_loyalty_empty_strans(monkeypatch, range_ab, card_profiles):
    cap = QueryCapture()
    cap.set_strans(lambda *a, **k: pd.DataFrame())
    monkeypatch.setattr("app.domain.loyalty_customers.query_strans", cap.query_strans)
    out = fetch_loyalty_customers(*range_ab)
    assert out.empty
    assert list(out.columns) == LOYALTY_METRIC_COLUMNS


def test_loyalty_uses_sql_group_by(monkeypatch, range_ab, card_profiles, loyalty_agg):
    cap = QueryCapture()
    _install(monkeypatch, cap, loyalty_agg, card_profiles)
    fetch_loyalty_customers(*range_ab)
    assert "GROUP BY" in (cap.strans_calls[0].get("sql_suffix") or "").upper()
    assert "SUM(" in cap.strans_calls[0]["body"].upper()


def test_loyalty_aggregate_points_and_bill_count(
    monkeypatch, range_ab, card_profiles, loyalty_agg
):
    cap = QueryCapture()
    _install(monkeypatch, cap, loyalty_agg, card_profiles)
    out = fetch_loyalty_customers(*range_ab)
    by = out.set_index("CARD_ID")
    assert by.loc["E10000000053", "total_value"] == pytest.approx(150_000.0)
    assert by.loc["E10000000053", "points"] == pytest.approx(points_of(150_000))
    assert by.loc["E10000000053", "bill_count"] == 2
    assert by.loc["A10000054973", "points"] == pytest.approx(12.0)
    assert by.loc["E10000000099", "points"] == pytest.approx(1.0)
    assert by.loc["E10000000053", "NAME_U"] == "Alice"


def test_loyalty_reaggregates_across_shards(monkeypatch, range_ab, card_profiles):
    """Same CARD_ID on two shard results must sum value/bills."""
    shard_rows = pd.DataFrame(
        [
            {"CARD_ID": "E10000000053", "STK_ID": "10001", "total_value": 100_000.0, "bill_count": 1},
            {"CARD_ID": "E10000000053", "STK_ID": "10004", "total_value": 50_000.0, "bill_count": 1},
        ]
    )
    cap = QueryCapture()
    _install(monkeypatch, cap, shard_rows, card_profiles)
    out = fetch_loyalty_customers(*range_ab)
    by = out.set_index("CARD_ID")
    assert by.loc["E10000000053", "total_value"] == pytest.approx(150_000.0)
    assert by.loc["E10000000053", "bill_count"] == 2


def test_loyalty_filter_mode_points_min_max(
    monkeypatch, range_ab, card_profiles, loyalty_agg
):
    cap = QueryCapture()
    _install(monkeypatch, cap, loyalty_agg, card_profiles)
    out = fetch_loyalty_customers(
        *range_ab, filter_mode="points", min_metric=2, max_metric=10
    )
    assert set(out["CARD_ID"]) == {"E10000000053"}


def test_loyalty_filter_mode_value(
    monkeypatch, range_ab, card_profiles, loyalty_agg
):
    cap = QueryCapture()
    _install(monkeypatch, cap, loyalty_agg, card_profiles)
    out = fetch_loyalty_customers(
        *range_ab, filter_mode="value", min_metric=100_000, max_metric=200_000
    )
    assert set(out["CARD_ID"]) == {"E10000000053"}


def test_loyalty_store_filter_in_sql(monkeypatch, range_ab, card_profiles, loyalty_agg):
    cap = QueryCapture()
    _install(monkeypatch, cap, loyalty_agg, card_profiles)
    fetch_loyalty_customers(*range_ab, store_ids=["10001", "10004"])
    assert cap.strans_calls
    where = cap.strans_calls[0]["extra_where"]
    assert_where_contains(where, "STK_ID")
    assert "10001" in cap.strans_calls[0]["extra_params"]
    assert "10004" in cap.strans_calls[0]["extra_params"]


def test_loyalty_prefix_in_sql_not_double_applied(
    monkeypatch, range_ab, card_profiles, loyalty_agg
):
    """Prefix goes to SQL; filter_frame_by_customer must get card_prefix=''."""
    cap = QueryCapture()
    _install(monkeypatch, cap, loyalty_agg, card_profiles)
    seen = {}

    import app.domain.loyalty_customers as mod

    real = mod.filter_frame_by_customer

    def wrap(df, **kwargs):
        seen.update(kwargs)
        return real(df, **kwargs)

    monkeypatch.setattr(mod, "filter_frame_by_customer", wrap)
    fetch_loyalty_customers(
        *range_ab, card_prefix="E", min_age=20, sex="F"
    )
    where = cap.strans_calls[0]["extra_where"]
    assert "CARD_ID" in where.upper()
    assert "LOWER" not in where.upper()  # fact prefix matcher
    assert seen.get("card_prefix") == ""


def test_loyalty_birth_month_and_sex(
    monkeypatch, range_ab, card_profiles, loyalty_agg
):
    cap = QueryCapture()
    _install(monkeypatch, cap, loyalty_agg, card_profiles)
    out = fetch_loyalty_customers(
        *range_ab, birth_month=7, sex="F", min_age=20
    )
    assert set(out["CARD_ID"]) == {"E10000000053", "E10000000099"}


def test_loyalty_points_divisor_constant():
    assert POINTS_DIVISOR == 50_000.0
    assert points_of(250_000) == pytest.approx(5.0)
    assert points_of(99_999) == pytest.approx(1.0)
    assert points_of(49_999) == pytest.approx(0.0)
    assert points_of(50_000) == pytest.approx(1.0)
