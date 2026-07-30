"""Client-side result sorting — applied after search, shared by preview + Excel export."""
from __future__ import annotations

import pandas as pd


def lead_and_sort(
    df: pd.DataFrame | None,
    *,
    lead: str | None = None,
    column: str | None = None,
    ascending: bool = True,
) -> pd.DataFrame:
    """
    Reorder columns (put ``lead`` first when present) then sort by ``column``
    (falls back to ``lead``). Does not mutate the input frame.
    """
    if df is None:
        return pd.DataFrame()
    if df.empty:
        out = df.copy()
        return _lead_columns(out, lead)

    out = df.copy()
    out = _lead_columns(out, lead)
    sort_col = column if column and column in out.columns else None
    if sort_col is None and lead and lead in out.columns:
        sort_col = lead
    if sort_col is None:
        return out.reset_index(drop=True)
    try:
        out = out.sort_values(
            sort_col,
            ascending=ascending,
            kind="mergesort",
            na_position="last",
        )
    except TypeError:
        # Mixed / unorderable types — coerce to string for stable UX
        key = out[sort_col].astype(str)
        out = out.assign(_sort_key=key).sort_values(
            "_sort_key",
            ascending=ascending,
            kind="mergesort",
            na_position="last",
        ).drop(columns=["_sort_key"])
    return out.reset_index(drop=True)


def _lead_columns(df: pd.DataFrame, lead: str | None) -> pd.DataFrame:
    if not lead or lead not in df.columns:
        return df
    cols = [lead] + [c for c in df.columns if c != lead]
    return df.loc[:, cols]


class ResultSort:
    """Mutable sort preference remembered across preview clicks / export."""

    def __init__(self, *, lead: str, ascending: bool = True):
        self.lead = lead
        self.column: str | None = lead
        self.ascending = ascending

    def sync_column_if_needed(self, df: pd.DataFrame | None) -> None:
        if df is None or df.empty:
            return
        cols = [str(c) for c in df.columns]
        if self.column not in cols:
            self.column = self.lead if self.lead in cols else (cols[0] if cols else None)

    def apply(self, df: pd.DataFrame | None) -> pd.DataFrame:
        self.sync_column_if_needed(df)
        return lead_and_sort(
            df,
            lead=self.lead,
            column=self.column,
            ascending=self.ascending,
        )

    def set_column(self, column: str, *, reset_ascending: bool = True) -> None:
        if reset_ascending and column != self.column:
            self.ascending = True
        self.column = column

    def toggle_column(self, column: str) -> None:
        if self.column == column:
            self.ascending = not self.ascending
        else:
            self.column = column
            self.ascending = True
