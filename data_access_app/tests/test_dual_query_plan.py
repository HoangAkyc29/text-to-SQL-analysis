"""Cutoff / dual-db planning — edge cases beyond the smoke suite."""
from __future__ import annotations

from datetime import date, datetime

import pytest

from app.db.cutoff import (
    STRANS_FROM_YM,
    archive_newest_ym,
    iter_year_months,
    rolling_cutoff,
    split_date_range,
)
from app.db.dual_query import plan_strans_parts, plan_transhdr_parts


def test_rolling_cutoff_january():
    now = datetime(2026, 1, 15, 8, 0, 0)
    assert rolling_cutoff(now) == date(2025, 12, 1)
    assert archive_newest_ym(now) == "202511"


def test_split_db1_only():
    now = datetime(2026, 7, 30)
    split = split_date_range(date(2026, 3, 1), date(2026, 5, 15), now=now)
    assert split.needs_db1 and not split.needs_db2
    assert split.db2_start is None
    assert split.db1_end == date(2026, 5, 15)
    assert "STRANS_202605" in split.strans_shards
    assert all(not s.endswith("202606") for s in split.strans_shards)


def test_split_exact_cutoff_is_db2_only_for_start():
    now = datetime(2026, 7, 30)
    # start == cutoff → no db1
    split = split_date_range(date(2026, 6, 1), date(2026, 6, 15), now=now)
    assert split.needs_db2 and not split.needs_db1


def test_split_end_day_before_cutoff_is_db1_only():
    now = datetime(2026, 7, 30)
    split = split_date_range(date(2026, 5, 1), date(2026, 5, 31), now=now)
    assert split.needs_db1 and not split.needs_db2


def test_split_rejects_inverted_range():
    with pytest.raises(ValueError, match="date_end"):
        split_date_range(date(2026, 7, 10), date(2026, 7, 1), now=datetime(2026, 7, 30))


def test_strans_shard_floor_clamped():
    now = datetime(2026, 7, 30)
    # start far before STRANS_FROM_YM
    split = split_date_range(date(2020, 1, 1), date(2024, 2, 15), now=now)
    assert split.needs_db1
    assert split.strans_shards[0] == f"STRANS_{STRANS_FROM_YM}"
    assert "STRANS_202311" not in split.strans_shards


def test_pmtrans_shards_start_later_than_strans():
    now = datetime(2026, 7, 30)
    split = split_date_range(date(2023, 12, 1), date(2024, 3, 15), now=now)
    assert split.strans_shards[0] == "STRANS_202312"
    assert split.pmtrans_shards[0] == "PMTRANS_202401"
    assert "PMTRANS_202312" not in split.pmtrans_shards


def test_iter_year_months_empty_when_inverted():
    assert iter_year_months("202406", "202405") == []


def test_plan_strans_cross_cutoff_tables_and_params():
    now = datetime(2026, 7, 30)
    split = split_date_range(date(2026, 4, 1), date(2026, 7, 15), now=now)
    body = "SELECT CARD_ID FROM {table} WHERE 1=1"
    parts = plan_strans_parts(split, body, extra_where="CARD_ID IS NOT NULL", extra_params=[])
    targets = [p[0] for p in parts]
    assert "db2" in targets and "db1" in targets
    db2 = next(p for p in parts if p[0] == "db2")
    import re

    assert re.search(r"FROM\s+STRANS\b", db2[1])
    assert not re.search(r"FROM\s+STRANS_\d+", db2[1])
    assert db2[2][0] == date(2026, 6, 1)
    assert db2[2][1] == date(2026, 7, 15)
    db1_parts = [p for p in parts if p[0] == "db1"]
    assert any("STRANS_202605" in p[1] for p in db1_parts)
    assert all("STRANS_202606" not in p[1] for p in db1_parts)


def test_plan_transhdr_uses_arc_not_monthly():
    now = datetime(2026, 7, 30)
    split = split_date_range(date(2026, 4, 1), date(2026, 7, 15), now=now)
    body = "SELECT TRANS_NUM FROM {table} WHERE 1=1"
    parts = plan_transhdr_parts(split, body)
    db1 = [p for p in parts if p[0] == "db1"]
    assert len(db1) == 1
    assert "TRANSHDR_ARC" in db1[0][1]
    assert "TRANSHDR_2026" not in db1[0][1]
    db2 = next(p for p in parts if p[0] == "db2")
    assert "FROM TRANSHDR" in db2[1].replace("\n", " ")
    assert "TRANSHDR_ARC" not in db2[1]
