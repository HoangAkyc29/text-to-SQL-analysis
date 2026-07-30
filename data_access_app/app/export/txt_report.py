"""Statistical TXT reports."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

import pandas as pd

from app.export.excel import write_txt
from pathlib import Path


def _header(title: str, meta: dict[str, str] | None = None) -> list[str]:
    lines = [
        "=" * 60,
        title,
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "=" * 60,
    ]
    for k, v in (meta or {}).items():
        lines.append(f"{k}: {v}")
    lines.append("")
    return lines


def age_years(birthday, as_of: datetime | None = None) -> float | None:
    if birthday is None or (isinstance(birthday, float) and pd.isna(birthday)):
        return None
    try:
        bd = pd.to_datetime(birthday)
    except Exception:  # noqa: BLE001
        return None
    if pd.isna(bd):
        return None
    ref = as_of or datetime.now()
    return (ref - bd.to_pydatetime()).days / 365.25


def build_stats_report(
    df: pd.DataFrame,
    *,
    title: str,
    meta: dict[str, str] | None = None,
    options: Iterable[str] | None = None,
    point_col: str = "points",
    value_col: str = "total_value",
    stk_col: str = "STK_ID",
    time_col: str = "TRAN_TIME",
    date_col: str = "TRAN_DATE",
    birthday_col: str = "BIRTHDAY",
) -> list[str]:
    opts = set(options or [])
    lines = _header(title, meta)
    if df is None or df.empty:
        lines.append("(không có dữ liệu)")
        return lines

    if "count" in opts or not opts:
        lines.append(f"[Số lượng] rows={len(df)}")
        if value_col in df.columns:
            lines.append(f"  sum({value_col})={pd.to_numeric(df[value_col], errors='coerce').sum():,.2f}")
        if point_col in df.columns:
            lines.append(f"  sum({point_col})={pd.to_numeric(df[point_col], errors='coerce').sum():,.2f}")
        lines.append("")

    if "by_points" in opts and point_col in df.columns:
        lines.append("[Theo điểm — histogram đơn giản]")
        s = pd.to_numeric(df[point_col], errors="coerce").dropna()
        if not s.empty:
            bins = [0, 50, 100, 200, 500, 1000, 5000, float("inf")]
            cats = pd.cut(s, bins=bins, right=False)
            for label, cnt in cats.value_counts().sort_index().items():
                lines.append(f"  {label}: {cnt}")
        lines.append("")

    if "by_store" in opts and stk_col in df.columns:
        lines.append("[Theo siêu thị STK_ID]")
        for stk, cnt in df[stk_col].astype(str).value_counts().items():
            lines.append(f"  {stk}: {cnt}")
        lines.append("")

    if "by_hour" in opts and time_col in df.columns:
        lines.append("[Theo giờ trong ngày]")
        hours = (
            df[time_col]
            .astype(str)
            .str.slice(0, 2)
            .replace({"na": None, "NaT": None})
        )
        for h, cnt in hours.value_counts().sort_index().items():
            lines.append(f"  {h}h: {cnt}")
        lines.append("")

    if "by_age" in opts and birthday_col in df.columns:
        lines.append("[Theo độ tuổi]")
        ages = df[birthday_col].map(age_years).dropna()
        if ages.empty:
            lines.append("  (không có BIRTHDAY)")
        else:
            bins = [0, 18, 25, 35, 45, 55, 65, 120]
            cats = pd.cut(ages, bins=bins, right=False)
            for label, cnt in cats.value_counts().sort_index().items():
                lines.append(f"  {label}: {cnt}")
        lines.append("")

    if "by_cycle" in opts and date_col in df.columns:
        lines.append("[Theo chu kỳ — tháng]")
        months = pd.to_datetime(df[date_col], errors="coerce").dt.to_period("M")
        for m, cnt in months.value_counts().sort_index().items():
            lines.append(f"  {m}: {cnt}")
        lines.append("")

    return lines


def write_stats(
    path: Path,
    df: pd.DataFrame,
    *,
    title: str,
    meta: dict[str, str] | None = None,
    options: Iterable[str] | None = None,
    **kwargs,
) -> Path:
    return write_txt(
        build_stats_report(df, title=title, meta=meta, options=options, **kwargs),
        path,
    )
