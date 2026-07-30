"""F1 / F6 product search (db2 master)."""
from __future__ import annotations

from typing import Any

import pandas as pd

from app.db.dual_query import master_select
from app.domain.columns import PRODUCT_COLUMNS
from app.domain.search_opts import (
    DEFAULT_SEARCH,
    SearchOpts,
    expand_params,
    mark_truncated,
    match_any,
    match_column,
    raise_if_truncated,
    resolve_search_limit,
)
from app.export.excel import project_columns


def search_products(
    *,
    code: str = "",
    name: str = "",
    limit: int | None = None,
    search: SearchOpts = DEFAULT_SEARCH,
) -> pd.DataFrame:
    code = (code or "").strip()
    name = (name or "").strip()
    lim = resolve_search_limit(limit)
    cols = ", ".join(PRODUCT_COLUMNS)
    clauses: list[str] = []
    params: list[Any] = []
    if code:
        code_cols = ["SKU_CODE", "SKU_ID", "BARCODE"]
        clauses.append(match_any(code_cols, search))
        params.extend(expand_params(code, len(code_cols), search))
    if name:
        clauses.append(match_column("FULL_NAME_U", search))
        params.extend(expand_params(name, 1, search))
    if not clauses:
        raise ValueError("Nhập mã hoặc tên mặt hàng")
    where = " AND ".join(f"({c})" for c in clauses)
    sql = f"SELECT TOP ({lim}) {cols} FROM SKU_DEF WHERE {where} ORDER BY SKU_CODE"
    out = project_columns(master_select(sql, params), PRODUCT_COLUMNS)
    return mark_truncated(out, lim)


def search_by_group(
    *,
    group_code: str = "",
    group_name: str = "",
    limit: int | None = None,
    search: SearchOpts = DEFAULT_SEARCH,
) -> pd.DataFrame:
    group_code = (group_code or "").strip()
    group_name = (group_name or "").strip()
    lim = resolve_search_limit(limit)
    cols = ", ".join(PRODUCT_COLUMNS)
    clauses: list[str] = []
    params: list[Any] = []
    if group_code:
        clauses.append(match_column("GRP_ID", search))
        params.extend(expand_params(group_code, 1, search))
    if group_name:
        clauses.append(match_column("GRP_NAME", search))
        params.extend(expand_params(group_name, 1, search))
    if not clauses:
        raise ValueError("Nhập mã nhóm hoặc tên nhóm")
    where = " AND ".join(clauses)
    sql = f"SELECT TOP ({lim}) {cols} FROM SKU_DEF WHERE {where} ORDER BY GRP_ID, SKU_CODE"
    out = project_columns(master_select(sql, params), PRODUCT_COLUMNS)
    return mark_truncated(out, lim)


def resolve_product_tokens(
    tokens: list[str],
    *,
    limit_per: int | None = None,
    search: SearchOpts = DEFAULT_SEARCH,
) -> dict[str, pd.DataFrame]:
    """Resolve each token as code OR name → SKU rows.

    Raises if a token hits the TOP cap (would silently drop SKUs in F4/F5).
    """
    out: dict[str, pd.DataFrame] = {}
    lim = resolve_search_limit(limit_per)
    for raw in tokens:
        token = raw.strip()
        if not token:
            continue
        df_code = search_products(code=token, limit=lim, search=search)
        df_name = search_products(name=token, limit=lim, search=search)
        raise_if_truncated(df_code, what=f"Mã/token {token!r}")
        raise_if_truncated(df_name, what=f"Tên/token {token!r}")
        frames = [f for f in (df_code, df_name) if f is not None and not f.empty]
        if frames:
            merged = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["SKU_ID"])
        else:
            merged = pd.DataFrame(columns=PRODUCT_COLUMNS)
        out[token] = mark_truncated(merged, lim)
    return out
