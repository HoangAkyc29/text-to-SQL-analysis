from __future__ import annotations

import pandas as pd

from project_core.domain.contracts.pipeline import ColumnStat, ResultProfile


def build_result_profile(df: pd.DataFrame) -> ResultProfile:
    columns: list[ColumnStat] = []
    for col in df.columns:
        series = df[col]
        columns.append(
            ColumnStat(
                name=str(col),
                null_pct=float(series.isna().mean()) if len(series) else 0.0,
                distinct_count=int(series.nunique(dropna=True)),
                min=series.min() if len(series) else None,
                max=series.max() if len(series) else None,
            )
        )
    flags: list[str] = []
    if len(df) == 0:
        flags.append("empty")
    if any(c.null_pct > 0.5 for c in columns):
        flags.append("high_null_rate")
    return ResultProfile(row_count=len(df), columns=columns, flags=flags)
