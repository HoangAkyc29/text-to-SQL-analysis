"""F2 customer / card search (db2 master)."""
from __future__ import annotations

from typing import Any

import pandas as pd

from app.db.dual_query import master_select
from app.domain.columns import CARD_LOOKUP_COLUMNS, CUSTOMER_COLUMNS
from app.domain.search_opts import (
    DEFAULT_SEARCH,
    SearchOpts,
    expand_params,
    expand_prefix_params,
    mark_truncated,
    match_any,
    match_column,
    match_prefix_column,
    resolve_search_limit,
)
from app.export.excel import project_columns
from app.text.tcvn3 import tcvn3_to_unicode


def _prefer_unicode_name(df: pd.DataFrame) -> pd.DataFrame:
    """Đưa tên Unicode vào cột NAME (ưu tiên NAME_U; không thì decode NAME)."""
    if df.empty or "NAME" not in df.columns:
        return df
    if "NAME_U" in df.columns:
        has_u = df["NAME_U"].notna() & (df["NAME_U"].astype(str).str.strip() != "")
        df.loc[has_u, "NAME"] = df.loc[has_u, "NAME_U"]
        df.loc[~has_u, "NAME"] = df.loc[~has_u, "NAME"].map(
            lambda v: tcvn3_to_unicode(v) if isinstance(v, str) else v
        )
    else:
        df["NAME"] = df["NAME"].map(
            lambda v: tcvn3_to_unicode(v) if isinstance(v, str) else v
        )
    return df


def search_customers(
    *,
    card_id: str = "",
    card_prefix: str = "",
    name: str = "",
    phone: str = "",
    birth_month: int | None = None,
    min_age: float | None = None,
    max_age: float | None = None,
    limit: int | None = None,
    search: SearchOpts = DEFAULT_SEARCH,
) -> pd.DataFrame:
    card_id = (card_id or "").strip()
    card_prefix = (card_prefix or "").strip()
    name = (name or "").strip()
    phone = (phone or "").strip()
    lim = resolve_search_limit(limit)

    # NAME_U chỉ đọc để coalesce → NAME; không export MOBI / DISC_LVL / dates
    cols = "CARD_ID, NAME_U, NAME, PHONE, SEX, BIRTHDAY, CUST_ID"
    clauses: list[str] = []
    params: list[Any] = []
    if card_id:
        clauses.append(match_column("CARD_ID", search))
        params.extend(expand_params(card_id, 1, search))
    if card_prefix:
        # Tiền tố = starts-with (prefix%), không phải substring %…%
        clauses.append(match_prefix_column("CARD_ID", search))
        params.extend(expand_prefix_params(card_prefix, 1, search))
    if name:
        name_cols = ["NAME_U", "NAME"]
        clauses.append(match_any(name_cols, search))
        params.extend(expand_params(name, len(name_cols), search))
    if phone:
        phone_cols = ["PHONE", "MOBI"]
        clauses.append(match_any(phone_cols, search))
        params.extend(expand_params(phone, len(phone_cols), search))
    if birth_month is not None:
        m = int(birth_month)
        if m < 1 or m > 12:
            raise ValueError("Tháng sinh phải từ 1–12")
        clauses.append("BIRTHDAY IS NOT NULL AND MONTH(BIRTHDAY) = ?")
        params.append(m)
    if min_age is not None or max_age is not None:
        # Age as of today (SQL Server) — same idea as export.txt_report.age_years
        age_sql = (
            "(YEAR(CAST(GETDATE() AS date)) - YEAR(BIRTHDAY) - "
            "CASE WHEN DATEADD(year, YEAR(CAST(GETDATE() AS date)) - YEAR(BIRTHDAY), BIRTHDAY) "
            "> CAST(GETDATE() AS date) THEN 1 ELSE 0 END)"
        )
        clauses.append("BIRTHDAY IS NOT NULL")
        if min_age is not None:
            clauses.append(f"{age_sql} >= ?")
            params.append(float(min_age))
        if max_age is not None:
            clauses.append(f"{age_sql} <= ?")
            params.append(float(max_age))
    if not clauses:
        raise ValueError("Nhập mã thẻ, tiền tố, tên, SĐT, tháng sinh hoặc độ tuổi")
    where = " AND ".join(clauses)
    sql = f"SELECT TOP ({lim}) {cols} FROM CSCARD WHERE {where} ORDER BY CARD_ID"
    df = _prefer_unicode_name(master_select(sql, params))
    out = project_columns(df, CUSTOMER_COLUMNS)
    return mark_truncated(out, lim)


def lookup_cards(card_ids: list[str]) -> pd.DataFrame:
    """Exact IN lookup (not a free-text search) — no SearchOpts."""
    ids = [c.strip() for c in card_ids if c and str(c).strip()]
    if not ids:
        return pd.DataFrame(columns=CARD_LOOKUP_COLUMNS)
    cols = """
        CARD_ID, NAME_U, NAME, PHONE, MOBI, SEX, BIRTHDAY,
        DISC_LVL, CUST_ID
    """
    frames: list[pd.DataFrame] = []
    for i in range(0, len(ids), 400):
        chunk = ids[i : i + 400]
        placeholders = ",".join("?" for _ in chunk)
        sql = f"SELECT {cols} FROM CSCARD WHERE CARD_ID IN ({placeholders})"
        frames.append(master_select(sql, chunk))
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=CARD_LOOKUP_COLUMNS)
    df = _prefer_unicode_name(df)
    return project_columns(df, CARD_LOOKUP_COLUMNS)
