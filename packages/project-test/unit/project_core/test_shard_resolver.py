"""Shard resolver unit tests."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from project_core.domain.sql.shard_resolver import (
    archive_newest_ym,
    physical_shard_map,
    rolling_cutoff,
    shards_for_range,
    suggest_query_plan,
    table_naming_context,
)

pytestmark = pytest.mark.unit


def test_rolling_cutoff_june_2026():
    assert rolling_cutoff(datetime(2026, 6, 22)) == date(2026, 5, 1)


def test_archive_newest_ym_rolls_with_as_of():
    assert archive_newest_ym(datetime(2026, 7, 15)) == "202605"
    assert archive_newest_ym(datetime(2026, 6, 22)) == "202604"


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


def test_shards_for_range_no_match_returns_empty():
    shards = shards_for_range(
        "STRANS",
        date(2026, 7, 1),
        date(2026, 7, 6),
        catalog={
            "logical_tables": {
                "STRANS": {
                    "physical_tables": ["STRANS_202512", "STRANS_202601", "STRANS_202604"],
                }
            }
        },
    )
    assert shards == []


def test_suggest_query_plan_recent_range_db2_only_no_shards():
    plan = suggest_query_plan(
        {"time_range": {"start": "2026-07-01", "end": "2026-07-06"}},
        now=datetime(2026, 7, 15),
    )
    assert plan.cutoff == date(2026, 6, 1)
    assert plan.needs_db1 is False
    assert plan.needs_db2 is True
    assert plan.shards == []
    assert plan.archive_newest_ym == "202605"


def test_suggest_query_plan_spanning_cutoff():
    plan = suggest_query_plan(
        {"filters": {"date_from": "2026-04-01", "date_to": "2026-06-15"}},
        now=datetime(2026, 6, 22),
    )
    assert plan.cutoff == date(2026, 5, 1)
    assert plan.needs_db1 is True
    assert plan.needs_db2 is True
    assert plan.union_hint is not None
    assert plan.archive_newest_ym == "202604"
    assert plan.shards == ["STRANS_202604"]


def test_physical_shard_map_ends_at_archive_newest():
    m = physical_shard_map(now=datetime(2026, 7, 15))
    assert m["STRANS"][-1] == "STRANS_202605"
    assert "STRANS_202607" not in m["STRANS"]
    assert m["CRDTRANS_ARC"] == ["CRDTRANS_ARC"]


def test_table_naming_context_db2_bare():
    ctx = table_naming_context(now=datetime(2026, 7, 15))
    assert ctx["archive_newest_ym"] == "202605"
    assert "Never append _YYYYMM on db2" in ctx["db2_naming"]
