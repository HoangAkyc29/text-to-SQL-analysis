"""Unit tests for cutoff / dual-db planning (no live SQL)."""
from __future__ import annotations

from datetime import date, datetime

from app.db.cutoff import archive_newest_ym, rolling_cutoff, split_date_range
from app.export.splitters import parse_point_buckets, split_by_point_buckets
from app.text.tcvn3 import is_unicode_text_column, tcvn3_to_unicode
import pandas as pd


def test_rolling_cutoff_july_2026():
    now = datetime(2026, 7, 30, 12, 0, 0)
    assert rolling_cutoff(now) == date(2026, 6, 1)
    assert archive_newest_ym(now) == "202605"


def test_split_crosses_cutoff():
    now = datetime(2026, 7, 30)
    split = split_date_range(date(2026, 4, 1), date(2026, 7, 15), now=now)
    assert split.needs_db1 and split.needs_db2
    assert split.db2_start == date(2026, 6, 1)
    assert split.db1_end == date(2026, 5, 31)
    assert "STRANS_202605" in split.strans_shards
    assert "STRANS_202606" not in split.strans_shards


def test_split_db2_only():
    now = datetime(2026, 7, 30)
    split = split_date_range(date(2026, 6, 10), date(2026, 7, 10), now=now)
    assert split.needs_db2 and not split.needs_db1
    assert split.strans_shards == []


def test_point_buckets():
    buckets = parse_point_buckets("0-200, 200-500, >500")
    assert len(buckets) == 3
    df = pd.DataFrame({"points": [10, 250, 900]})
    parts = split_by_point_buckets(df, buckets)
    assert len(parts["0-200"]) == 1
    assert len(parts["200-500"]) == 1
    assert len(parts[">=500"]) == 1


def test_tcvn3_roundtrip_safe_on_unicode_col():
    assert is_unicode_text_column("FULL_NAME_U")
    assert tcvn3_to_unicode("abc") == "abc"
