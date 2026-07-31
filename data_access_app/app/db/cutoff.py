"""Rolling cutoff + db1 monthly shard expansion (standalone port)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


def _ref(now: datetime | None = None) -> datetime:
    """Session TRANSHDR as-of when now is omitted; else explicit override (tests)."""
    if now is not None:
        return now
    from app.db.session_clock import session_now

    return session_now()


def rolling_cutoff(now: datetime | None = None) -> date:
    """First day of the previous calendar month (relative to session/as-of)."""
    ref = _ref(now)
    year, month = ref.year, ref.month
    if month == 1:
        return date(year - 1, 12, 1)
    return date(year, month - 1, 1)


def archive_newest_ym(now: datetime | None = None) -> str:
    """YYYYMM of newest db1 archive month (month before cutoff)."""
    cutoff = rolling_cutoff(now)
    if cutoff.month == 1:
        return f"{cutoff.year - 1}12"
    return f"{cutoff.year}{cutoff.month - 1:02d}"


def _parse_ym(ym: str) -> tuple[int, int]:
    return int(ym[:4]), int(ym[4:6])


def _ym_str(year: int, month: int) -> str:
    return f"{year}{month:02d}"


def date_to_ym(d: date) -> str:
    return f"{d.year}{d.month:02d}"


def iter_year_months(from_ym: str, to_ym: str) -> list[str]:
    if not from_ym or not to_ym or from_ym > to_ym:
        return []
    y, m = _parse_ym(from_ym)
    ey, em = _parse_ym(to_ym)
    out: list[str] = []
    while (y, m) <= (ey, em):
        out.append(_ym_str(y, m))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


# Earliest shard suffixes known from data_dictionary/db1/shards.yaml
STRANS_FROM_YM = "202312"
PMTRANS_FROM_YM = "202401"


@dataclass(frozen=True)
class DateSplit:
    date_start: date
    date_end: date
    cutoff: date
    needs_db1: bool
    needs_db2: bool
    db1_start: date | None
    db1_end: date | None
    db2_start: date | None
    db2_end: date | None
    archive_newest_ym: str
    strans_shards: list[str]
    pmtrans_shards: list[str]


def split_date_range(
    date_start: date,
    date_end: date,
    *,
    now: datetime | None = None,
) -> DateSplit:
    if date_end < date_start:
        raise ValueError("date_end must be >= date_start")
    cutoff = rolling_cutoff(now)
    end_ym = archive_newest_ym(now)

    needs_db2 = date_end >= cutoff
    needs_db1 = date_start < cutoff

    db2_start = db2_end = None
    if needs_db2:
        db2_start = max(date_start, cutoff)
        db2_end = date_end

    db1_start = db1_end = None
    strans_shards: list[str] = []
    pmtrans_shards: list[str] = []
    if needs_db1:
        db1_start = date_start
        db1_end = min(date_end, cutoff.fromordinal(cutoff.toordinal() - 1))
        from_ym = max(STRANS_FROM_YM, date_to_ym(db1_start))
        to_ym = min(end_ym, date_to_ym(db1_end))
        months = iter_year_months(from_ym, to_ym)
        strans_shards = [f"STRANS_{ym}" for ym in months]
        pm_from = max(PMTRANS_FROM_YM, date_to_ym(db1_start))
        pm_months = iter_year_months(pm_from, to_ym)
        pmtrans_shards = [f"PMTRANS_{ym}" for ym in pm_months]

    return DateSplit(
        date_start=date_start,
        date_end=date_end,
        cutoff=cutoff,
        needs_db1=needs_db1,
        needs_db2=needs_db2,
        db1_start=db1_start,
        db1_end=db1_end,
        db2_start=db2_start,
        db2_end=db2_end,
        archive_newest_ym=end_ym,
        strans_shards=strans_shards,
        pmtrans_shards=pmtrans_shards,
    )
