"""Dual-DB fact queries: db2 bare + db1 shards, merge in pandas."""
from __future__ import annotations

from datetime import date
from typing import Any, Callable

import pandas as pd

from app.db import connection as db
from app.db.cutoff import DateSplit, split_date_range
from app.text.tcvn3 import decode_dataframe


ProgressCb = Callable[[str], None]


def _noop(_: str) -> None:
    return None


def _date_clause(alias: str = "") -> str:
    col = f"{alias}TRAN_DATE" if alias else "TRAN_DATE"
    return f"CAST({col} AS date) >= ? AND CAST({col} AS date) <= ?"


def run_selects(
    parts: list[tuple[str, str, list[Any]]],
    *,
    progress: ProgressCb | None = None,
    decode: bool = True,
) -> pd.DataFrame:
    """Execute (target, sql, params) parts and concat."""
    cb = progress or _noop
    frames: list[pd.DataFrame] = []
    for i, (target, sql, params) in enumerate(parts, start=1):
        cb(f"Query {i}/{len(parts)} trên {target}…")
        try:
            df = db.read_sql(target, sql, params)
        except Exception as exc:  # noqa: BLE001
            # Missing shard table is common at range edges — skip empty.
            msg = str(exc).lower()
            if "invalid object name" in msg or "does not exist" in msg:
                cb(f"Bỏ qua bảng không tồn tại ({target}): {exc}")
                continue
            raise
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
) -> list[tuple[str, str, list[Any]]]:
    """
    select_sql_body example:
      SELECT STK_ID, TRANS_NUM, ... FROM {table} WHERE 1=1
    Placeholders {table} replaced per physical table.
    Date filter appended automatically.
    """
    extra_params = list(extra_params or [])
    parts: list[tuple[str, str, list[Any]]] = []
    where_extra = f" AND ({extra_where})" if extra_where.strip() else ""

    if split.needs_db2 and split.db2_start and split.db2_end:
        sql = (
            select_sql_body.format(table="STRANS")
            + f" AND {_date_clause()}"
            + where_extra
        )
        params = [split.db2_start, split.db2_end, *extra_params]
        parts.append(("db2", sql, params))

    if split.needs_db1 and split.db1_start and split.db1_end:
        for phys in split.strans_shards:
            sql = (
                select_sql_body.format(table=phys)
                + f" AND {_date_clause()}"
                + where_extra
            )
            params = [split.db1_start, split.db1_end, *extra_params]
            parts.append(("db1", sql, params))
    return parts


def plan_transhdr_parts(
    split: DateSplit,
    select_sql_body: str,
    *,
    extra_where: str = "",
    extra_params: list[Any] | None = None,
) -> list[tuple[str, str, list[Any]]]:
    extra_params = list(extra_params or [])
    parts: list[tuple[str, str, list[Any]]] = []
    where_extra = f" AND ({extra_where})" if extra_where.strip() else ""

    if split.needs_db2 and split.db2_start and split.db2_end:
        sql = (
            select_sql_body.format(table="TRANSHDR")
            + f" AND {_date_clause()}"
            + where_extra
        )
        params = [split.db2_start, split.db2_end, *extra_params]
        parts.append(("db2", sql, params))

    if split.needs_db1 and split.db1_start and split.db1_end:
        sql = (
            select_sql_body.format(table="TRANSHDR_ARC")
            + f" AND {_date_clause()}"
            + where_extra
        )
        params = [split.db1_start, split.db1_end, *extra_params]
        parts.append(("db1", sql, params))
    return parts


def query_strans(
    date_start: date,
    date_end: date,
    select_sql_body: str,
    *,
    extra_where: str = "",
    extra_params: list[Any] | None = None,
    progress: ProgressCb | None = None,
) -> pd.DataFrame:
    split = split_date_range(date_start, date_end)
    parts = plan_strans_parts(
        split, select_sql_body, extra_where=extra_where, extra_params=extra_params
    )
    return run_selects(parts, progress=progress)


def query_transhdr(
    date_start: date,
    date_end: date,
    select_sql_body: str,
    *,
    extra_where: str = "",
    extra_params: list[Any] | None = None,
    progress: ProgressCb | None = None,
) -> pd.DataFrame:
    split = split_date_range(date_start, date_end)
    parts = plan_transhdr_parts(
        split, select_sql_body, extra_where=extra_where, extra_params=extra_params
    )
    return run_selects(parts, progress=progress)


def master_select(sql: str, params: list[Any] | None = None) -> pd.DataFrame:
    """Always db2 for master tables."""
    return decode_dataframe(db.read_sql("db2", sql, params))
