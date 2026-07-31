"""Process-lifetime 'now' for cutoff — newest TRANSHDR on db2 at app start."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import pandas as pd

from app.db import connection as db


@dataclass(frozen=True)
class SessionClockStatus:
    as_of: datetime
    source: str  # "transhdr" | "wall"
    detail: str


_as_of: datetime | None = None
_source: str = "wall"
_detail: str = "chưa khởi tạo"
_bootstrapped: bool = False


def session_now() -> datetime:
    """Reference time for rolling_cutoff until process exit / explicit refresh."""
    return _as_of if _as_of is not None else datetime.now()


def status() -> SessionClockStatus:
    return SessionClockStatus(
        as_of=session_now(),
        source=_source,
        detail=_detail,
    )


def _coerce_as_of(value: Any) -> datetime | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    # pandas Timestamp / string
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return None
    py = ts.to_pydatetime()
    if getattr(py, "tzinfo", None) is not None:
        py = py.replace(tzinfo=None)
    return py


def fetch_newest_transhdr_as_of() -> datetime:
    """
    Newest TRAN_DATE on live TRANSHDR (db2).
    Raises DbError / ValueError if unavailable or empty.
    """
    df = db.read_sql(
        "db2",
        """
        SELECT MAX(TRAN_DATE) AS max_tran_date
        FROM TRANSHDR
        WHERE TRAN_DATE IS NOT NULL
        """,
    )
    if df is None or df.empty:
        raise ValueError("TRANSHDR không trả về dòng")
    raw = df.iloc[0].get("max_tran_date")
    as_of = _coerce_as_of(raw)
    if as_of is None:
        raise ValueError("TRANSHDR.MAX(TRAN_DATE) trống / không parse được")
    return as_of


def refresh_from_transhdr() -> SessionClockStatus:
    """Re-read MAX(TRAN_DATE) from db2 TRANSHDR and pin as session clock."""
    global _as_of, _source, _detail, _bootstrapped
    try:
        as_of = fetch_newest_transhdr_as_of()
        _as_of = as_of
        _source = "transhdr"
        _detail = f"MAX(TRANSHDR.TRAN_DATE) db2 = {as_of.isoformat(sep=' ', timespec='seconds')}"
        _bootstrapped = True
        print(f"DATA_ACCESS_AS_OF={_as_of.isoformat()} source=transhdr", flush=True)
    except Exception as exc:  # noqa: BLE001
        _as_of = datetime.now()
        _source = "wall"
        _detail = f"Fallback đồng hồ máy (không lấy được TRANSHDR): {exc}"
        _bootstrapped = True
        print(f"DATA_ACCESS_AS_OF={_as_of.isoformat()} source=wall err={exc}", flush=True)
    return status()


def bootstrap_session_clock(*, force: bool = False) -> SessionClockStatus:
    """Call once at process start (idempotent unless force=True)."""
    global _bootstrapped
    if _bootstrapped and not force:
        return status()
    return refresh_from_transhdr()


def reset_to_wall_clock() -> SessionClockStatus:
    """Explicit reset: use machine time until next refresh_from_transhdr."""
    global _as_of, _source, _detail, _bootstrapped
    _as_of = datetime.now()
    _source = "wall"
    _detail = "Đã reset về đồng hồ máy (wall clock)"
    _bootstrapped = True
    print(f"DATA_ACCESS_AS_OF={_as_of.isoformat()} source=wall reset=1", flush=True)
    return status()
