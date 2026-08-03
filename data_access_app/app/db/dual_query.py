"""Dual-DB fact queries: db2 bare + db1 shards, merge in pandas."""
from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta
from typing import Any, Callable

import pandas as pd

from app.db import connection as db
from app.db.cutoff import DateSplit, split_date_range
from app.db.errors import DbError, is_missing_object_error, wrap_db_exception
from app.text.tcvn3 import decode_dataframe


ProgressCb = Callable[[str], None]


def _noop(_: str) -> None:
    return None


def _date_clause(alias: str = "") -> str:
    """Sargable half-open range: col >= start AND col < end_exclusive.

    Avoids CAST(TRAN_DATE AS date) which blocks index range seeks.
    """
    col = f"{alias}TRAN_DATE" if alias else "TRAN_DATE"
    return f"{col} >= ? AND {col} < ?"


def _date_params(start: date, end: date) -> list[date]:
    """Inclusive calendar end → exclusive upper bound (end + 1 day)."""
    return [start, end + timedelta(days=1)]


def _clip_month(ym: str, start: date, end: date) -> tuple[date, date] | None:
    """Clip [start, end] to calendar month of ``YYYYMM`` shard; None if no overlap."""
    if len(ym) != 6 or not ym.isdigit():
        return start, end
    year, month = int(ym[:4]), int(ym[4:6])
    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])
    lo = max(start, month_start)
    hi = min(end, month_end)
    if lo > hi:
        return None
    return lo, hi


def run_selects(
    parts: list[tuple[str, str, list[Any]]],
    *,
    progress: ProgressCb | None = None,
    decode: bool = True,
) -> pd.DataFrame:
    """Execute (target, sql, params) parts and concat.

    - Missing shard table → skip (range edges).
    - Disconnect / restore / timeout → raise DbError (do not pretend empty success).
    """
    cb = progress or _noop
    frames: list[pd.DataFrame] = []
    if not parts:
        return pd.DataFrame()

    for i, (target, sql, params) in enumerate(parts, start=1):
        cb(f"Query {i}/{len(parts)} trên {target}…")
        try:
            df = db.read_sql(target, sql, params)
        except DbError:
            raise
        except Exception as exc:  # noqa: BLE001
            if is_missing_object_error(exc):
                cb(f"Bỏ qua bảng không tồn tại ({target}): {exc}")
                continue
            raise wrap_db_exception(exc, target=target) from exc
        if df is not None and not df.empty:
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    return decode_dataframe(out) if decode else out


def plan_strans_parts(
    split: DateSplit,
    select_sql_body: str,
    *,
    extra_where: str = "",
    extra_params: list[Any] | None = None,
    sql_suffix: str = "",
) -> list[tuple[str, str, list[Any]]]:
    """
    select_sql_body example:
      SELECT STK_ID, TRANS_NUM, ... FROM {table} WHERE 1=1
    Placeholders {table} replaced per physical table.
    Date filter appended automatically (sargable half-open range).
    db1 shard date params are clipped to that month.
    ``sql_suffix`` is appended after WHERE (e.g. `` GROUP BY ...``).
    """
    extra_params = list(extra_params or [])
    parts: list[tuple[str, str, list[Any]]] = []
    where_extra = f" AND ({extra_where})" if extra_where.strip() else ""
    suffix = f" {sql_suffix.strip()}" if sql_suffix and sql_suffix.strip() else ""

    if split.needs_db2 and split.db2_start and split.db2_end:
        sql = (
            select_sql_body.format(table="STRANS")
            + f" AND {_date_clause()}"
            + where_extra
            + suffix
        )
        params = [*_date_params(split.db2_start, split.db2_end), *extra_params]
        parts.append(("db2", sql, params))

    if split.needs_db1 and split.db1_start and split.db1_end:
        for phys in split.strans_shards:
            ym = phys.rsplit("_", 1)[-1] if "_" in phys else ""
            clipped = _clip_month(ym, split.db1_start, split.db1_end)
            if clipped is None:
                continue
            lo, hi = clipped
            sql = (
                select_sql_body.format(table=phys)
                + f" AND {_date_clause()}"
                + where_extra
                + suffix
            )
            params = [*_date_params(lo, hi), *extra_params]
            parts.append(("db1", sql, params))
    return parts


def plan_transhdr_parts(
    split: DateSplit,
    select_sql_body: str,
    *,
    extra_where: str = "",
    extra_params: list[Any] | None = None,
    sql_suffix: str = "",
) -> list[tuple[str, str, list[Any]]]:
    extra_params = list(extra_params or [])
    parts: list[tuple[str, str, list[Any]]] = []
    where_extra = f" AND ({extra_where})" if extra_where.strip() else ""
    suffix = f" {sql_suffix.strip()}" if sql_suffix and sql_suffix.strip() else ""

    if split.needs_db2 and split.db2_start and split.db2_end:
        sql = (
            select_sql_body.format(table="TRANSHDR")
            + f" AND {_date_clause()}"
            + where_extra
            + suffix
        )
        params = [*_date_params(split.db2_start, split.db2_end), *extra_params]
        parts.append(("db2", sql, params))

    if split.needs_db1 and split.db1_start and split.db1_end:
        sql = (
            select_sql_body.format(table="TRANSHDR_ARC")
            + f" AND {_date_clause()}"
            + where_extra
            + suffix
        )
        params = [*_date_params(split.db1_start, split.db1_end), *extra_params]
        parts.append(("db1", sql, params))
    return parts


def query_strans(
    date_start: date,
    date_end: date,
    select_sql_body: str,
    *,
    extra_where: str = "",
    extra_params: list[Any] | None = None,
    sql_suffix: str = "",
    progress: ProgressCb | None = None,
) -> pd.DataFrame:
    split = split_date_range(date_start, date_end)
    parts = plan_strans_parts(
        split,
        select_sql_body,
        extra_where=extra_where,
        extra_params=extra_params,
        sql_suffix=sql_suffix,
    )
    return run_selects(parts, progress=progress)


def query_transhdr(
    date_start: date,
    date_end: date,
    select_sql_body: str,
    *,
    extra_where: str = "",
    extra_params: list[Any] | None = None,
    sql_suffix: str = "",
    progress: ProgressCb | None = None,
) -> pd.DataFrame:
    split = split_date_range(date_start, date_end)
    parts = plan_transhdr_parts(
        split,
        select_sql_body,
        extra_where=extra_where,
        extra_params=extra_params,
        sql_suffix=sql_suffix,
    )
    return run_selects(parts, progress=progress)


def master_select(sql: str, params: list[Any] | None = None) -> pd.DataFrame:
    """Always db2 for master tables."""
    try:
        return decode_dataframe(db.read_sql("db2", sql, params))
    except DbError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise wrap_db_exception(exc, target="db2") from exc
