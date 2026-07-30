"""Split dataframes by buckets / keys."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class PointBucket:
    label: str
    lo: float
    hi: float | None  # None = open-ended >= lo


def parse_point_buckets(text: str) -> list[PointBucket]:
    """
    Parse user buckets like:
      0-200, 200-500, >500
      0:200;200:500;500:
    """
    raw = text.strip()
    if not raw:
        return []
    parts = re_split(raw)
    buckets: list[PointBucket] = []
    for part in parts:
        p = part.strip()
        if not p:
            continue
        if p.startswith(">") or p.startswith("≥"):
            lo = float(p.lstrip(">≥").strip())
            buckets.append(PointBucket(label=f">={lo:g}", lo=lo, hi=None))
            continue
        if "-" in p or ":" in p or "–" in p:
            sep = "-" if "-" in p else (":" if ":" in p else "–")
            a, b = p.split(sep, 1)
            a, b = a.strip(), b.strip()
            lo = float(a) if a else 0.0
            if b == "" or b.upper() in {"INF", "∞"}:
                buckets.append(PointBucket(label=f">={lo:g}", lo=lo, hi=None))
            else:
                hi = float(b)
                buckets.append(PointBucket(label=f"{lo:g}-{hi:g}", lo=lo, hi=hi))
            continue
        raise ValueError(f"Không parse được bucket: {p}")
    return buckets


def re_split(raw: str) -> list[str]:
    import re

    return re.split(r"[,;|/]+", raw)


def assign_bucket(points: float, buckets: list[PointBucket]) -> str | None:
    for b in buckets:
        if b.hi is None:
            if points >= b.lo:
                return b.label
        elif b.lo <= points < b.hi:
            return b.label
    return None


def split_by_point_buckets(df: pd.DataFrame, buckets: list[PointBucket], col: str = "points") -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {b.label: df.iloc[0:0].copy() for b in buckets}
    if df is None or df.empty:
        return out
    for b in buckets:
        if b.hi is None:
            mask = df[col] >= b.lo
        else:
            mask = (df[col] >= b.lo) & (df[col] < b.hi)
        out[b.label] = df.loc[mask].copy()
    return out


def split_by_column(df: pd.DataFrame, column: str) -> dict[str, pd.DataFrame]:
    if df is None or df.empty or column not in df.columns:
        return {}
    out: dict[str, pd.DataFrame] = {}
    for key, group in df.groupby(column, dropna=False):
        label = "NULL" if pd.isna(key) else str(key).strip() or "EMPTY"
        out[label] = group.copy()
    return out
