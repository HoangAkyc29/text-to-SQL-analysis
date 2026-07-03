"""Shard resolver unit tests."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from project_core.domain.sql.shard_resolver import rolling_cutoff, shards_for_range, suggest_query_plan

pytestmark = pytest.mark.unit


def test_rolling_cutoff_june_2026():
    assert rolling_cutoff(datetime(2026, 6, 22)) == date(2026, 5, 1)


def test_shards_for_range_filters_by_month():
    shards = shards_for_range(
        "STRANS",
        date(2026, 1, 1),
        date(2026, 3, 31),
        catalog={
            "logical_tables": {
                "STRANS": {
                    "physical_tables": ["STRANS_202512", "STRANS_202601", "STRANS_202602", "STRANS_202603"],
                }
            }
        },
    )
    assert "STRANS_202601" in shards
    assert "STRANS_202512" not in shards


def test_suggest_query_plan_spanning_cutoff():
    plan = suggest_query_plan(
        {"filters": {"date_from": "2026-04-01", "date_to": "2026-06-15"}},
        now=datetime(2026, 6, 22),
    )
    assert plan.cutoff == date(2026, 5, 1)
    assert plan.needs_db1 is True
    assert plan.needs_db2 is True
    assert plan.union_hint is not None
