"""F5 — orders containing product token(s) in A–B.

Mode 1 (orders): TRANSHDR — one row per (STK_ID, TRANS_NUM) that contains the seed SKU.
Mode 2 (bill_lines): full STRANS for those bills (every item in the transaction).

Empty product list → all bills in the date window via STRANS DISTINCT keys
(STK_ID correct) + TRANSHDR bill_value (same store/card/gift/value filters).
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Callable, Literal

import pandas as pd

from app.db.dual_query import query_strans
from app.domain.bill_expand import bill_keys_from_lines, fetch_bill_lines, fetch_transhdr_for_keys
from app.domain.columns import (
    BILL_VALUE_SQL,
    CUSTOMER_COLUMNS,
    F5_ORDER_LINE_COLUMNS,
    ORDER_COLUMNS,
)
from app.domain.customer import lookup_cards
from app.domain.customer_filters import SexFilter, customer_filters_active, filter_frame_by_customer
from app.domain.product import resolve_product_tokens
from app.domain.search_opts import (
    DEFAULT_SEARCH,
    SearchOpts,
    expand_prefix_params,
    match_prefix_column_fact,
)
from app.export.excel import project_columns, sanitize_filename, write_excel, write_excel_multi
from app.domain.frame_sort import lead_and_sort
from app.export.rich_report import build_orders_rich_report, write_rich_lines
from app.export.splitters import split_by_column

ProgressCb = Callable[[str], None]
GiftMode = Literal["any", "paid", "gift"]

# Synthetic bucket when the product list is blank (all SKUs in A–B).
ALL_PRODUCTS_LABEL = "(tất cả SP)"


def enrich_order_headers(df: pd.DataFrame) -> pd.DataFrame:
    """Attach NAME_U from CSCARD onto TRANSHDR-style rows."""
    if df is None or df.empty:
        return pd.DataFrame(columns=ORDER_COLUMNS)
    kept = df.copy()
    if "CARD_ID" not in kept.columns:
        kept["NAME_U"] = ""
        return project_columns(kept, ORDER_COLUMNS)
    card_ids = (
        kept["CARD_ID"]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .unique()
        .tolist()
    )
    if card_ids:
        cdf = lookup_cards(card_ids)
        if not cdf.empty and "NAME_U" in cdf.columns:
            drop_n = [c for c in ("NAME_U",) if c in kept.columns]
            if drop_n:
                kept = kept.drop(columns=drop_n)
            kept = kept.merge(cdf[["CARD_ID", "NAME_U"]], on="CARD_ID", how="left")
    if "NAME_U" not in kept.columns:
        kept["NAME_U"] = ""
    return project_columns(kept, ORDER_COLUMNS)


def _apply_order_post_filters(
    orders: pd.DataFrame,
    *,
    date_end: date,
    min_bill: float | None,
    max_bill: float | None,
    min_age: float | None,
    max_age: float | None,
    sex: SexFilter,
    birth_month: int | None,
    card_prefix: str,
    search: SearchOpts,
    progress: ProgressCb | None,
) -> pd.DataFrame:
    cb = progress or (lambda _: None)
    if orders is None or orders.empty:
        return pd.DataFrame(columns=ORDER_COLUMNS)
    orders = orders.copy()
    orders["bill_value"] = pd.to_numeric(orders.get("bill_value"), errors="coerce").fillna(0.0)
    if min_bill is not None:
        orders = orders.loc[orders["bill_value"] >= float(min_bill)]
    if max_bill is not None:
        orders = orders.loc[orders["bill_value"] <= float(max_bill)]
    if orders.empty:
        return pd.DataFrame(columns=ORDER_COLUMNS)

    orders = enrich_order_headers(orders)
    cust_on = customer_filters_active(
        min_age=min_age,
        max_age=max_age,
        sex=sex,
        birth_month=birth_month,
        card_prefix=card_prefix,
    )
    if cust_on:
        cb("Đang lọc theo điều kiện khách (tuổi / giới tính / tháng sinh / tiền tố)…")
        orders = filter_frame_by_customer(
            orders,
            min_age=min_age,
            max_age=max_age,
            sex=sex,
            birth_month=birth_month,
            card_prefix="",  # already applied in SQL when set
            as_of=date_end,
            search=search,
        )
        orders = project_columns(orders, ORDER_COLUMNS)
    return orders


def _common_fact_filters(
    *,
    store_ids: list[str] | None,
    require_card: bool,
    gift_mode: GiftMode,
    card_prefix: str,
    search: SearchOpts,
    apply_gift: bool,
    apply_store: bool,
) -> tuple[list[str], list]:
    extra: list[str] = []
    params: list = []
    stores = [s.strip() for s in (store_ids or []) if s and str(s).strip()]
    if apply_store and stores:
        sph = ",".join("?" for _ in stores)
        extra.append(f"LTRIM(RTRIM(STK_ID)) IN ({sph})")
        params.extend(stores)
    if require_card:
        extra.append("CARD_ID IS NOT NULL AND LTRIM(RTRIM(CARD_ID)) <> ''")
    if apply_gift:
        if gift_mode == "paid":
            extra.append("ISNULL(AMOUNT,0) > 0")
        elif gift_mode == "gift":
            extra.append("ISNULL(AMOUNT,0) = 0")
    if (card_prefix or "").strip():
        extra.append(match_prefix_column_fact("CARD_ID", search))
        params.extend(expand_prefix_params(card_prefix, 1, search))
    return extra, params


def _orders_all_in_period(
    date_start: date,
    date_end: date,
    *,
    store_ids: list[str] | None,
    require_card: bool,
    min_bill: float | None,
    max_bill: float | None,
    gift_mode: GiftMode,
    progress: ProgressCb | None,
    min_age: float | None,
    max_age: float | None,
    sex: SexFilter,
    birth_month: int | None,
    card_prefix: str,
    search: SearchOpts,
) -> pd.DataFrame:
    """All bills in A–B (empty product list).

    Always discover ``(STK_ID, TRANS_NUM, TRANS_CODE)`` via ``SELECT DISTINCT`` on
    STRANS (HDR.STK_ID is blank in this domain), then load ``bill_value`` from
    TRANSHDR. Never stream every STRANS line amount — only distinct keys.
    """
    cb = progress or (lambda _: None)
    cust_on = customer_filters_active(
        min_age=min_age,
        max_age=max_age,
        sex=sex,
        birth_month=birth_month,
        card_prefix=card_prefix,
    )
    if cust_on:
        require_card = True

    cb("Không lọc SKU — DISTINCT khóa đơn trên STRANS (STK đúng)…")
    extra, params = _common_fact_filters(
        store_ids=store_ids,
        require_card=require_card,
        gift_mode=gift_mode,
        card_prefix=card_prefix,
        search=search,
        apply_gift=True,
        apply_store=True,
    )
    body = """
        SELECT DISTINCT
            LTRIM(RTRIM(STK_ID)) AS STK_ID,
            LTRIM(RTRIM(TRANS_NUM)) AS TRANS_NUM,
            LTRIM(RTRIM(TRANS_CODE)) AS TRANS_CODE
        FROM {table}
        WHERE 1=1
    """
    keys = query_strans(
        date_start,
        date_end,
        body,
        extra_where=" AND ".join(extra) if extra else "",
        extra_params=params,
        progress=progress,
    )
    if keys is None or keys.empty:
        return pd.DataFrame(columns=ORDER_COLUMNS)

    cb("Đang lấy TRANSHDR đại diện đơn…")
    orders = fetch_transhdr_for_keys(date_start, date_end, keys, progress=progress)
    return _apply_order_post_filters(
        orders,
        date_end=date_end,
        min_bill=min_bill,
        max_bill=max_bill,
        min_age=min_age,
        max_age=max_age,
        sex=sex,
        birth_month=birth_month,
        card_prefix=card_prefix,
        search=search,
        progress=progress,
    )


def _seed_lines_for_skus(
    date_start: date,
    date_end: date,
    sku_ids: list[str],
    *,
    store_ids: list[str] | None,
    require_card: bool,
    gift_mode: GiftMode,
    card_prefix: str,
    search: SearchOpts,
    progress: ProgressCb | None,
) -> pd.DataFrame:
    """One STRANS pull for all seed SKUs (shared by multi-token F5)."""
    if not sku_ids:
        return pd.DataFrame()
    cb = progress or (lambda _: None)
    extra, params = _common_fact_filters(
        store_ids=store_ids,
        require_card=require_card,
        gift_mode=gift_mode,
        card_prefix=card_prefix,
        search=search,
        apply_gift=True,
        apply_store=True,
    )
    ph = ",".join("?" for _ in sku_ids)
    extra = [f"LTRIM(RTRIM(SKU_ID)) IN ({ph})", *extra]
    params = [*sku_ids, *params]
    body = f"""
        SELECT
            LTRIM(RTRIM(STK_ID)) AS STK_ID,
            LTRIM(RTRIM(TRANS_NUM)) AS TRANS_NUM,
            TRAN_DATE,
            TRAN_TIME,
            LTRIM(RTRIM(CARD_ID)) AS CARD_ID,
            LTRIM(RTRIM(TRANS_CODE)) AS TRANS_CODE,
            LTRIM(RTRIM(SKU_ID)) AS SKU_ID,
            {BILL_VALUE_SQL} AS line_total
        FROM {{table}}
        WHERE 1=1
    """
    cb(f"Đang tìm đơn có SP ({len(sku_ids)} SKU, 1 lần STRANS)…")
    return query_strans(
        date_start,
        date_end,
        body,
        extra_where=" AND ".join(extra),
        extra_params=params,
        progress=progress,
    )


def _orders_from_seed_lines(
    date_start: date,
    date_end: date,
    lines: pd.DataFrame,
    *,
    min_bill: float | None,
    max_bill: float | None,
    min_age: float | None,
    max_age: float | None,
    sex: SexFilter,
    birth_month: int | None,
    card_prefix: str,
    search: SearchOpts,
    progress: ProgressCb | None,
) -> pd.DataFrame:
    cb = progress or (lambda _: None)
    if lines is None or lines.empty:
        return pd.DataFrame(columns=ORDER_COLUMNS)

    bill_keys = (
        lines[["STK_ID", "TRANS_NUM", "TRANS_CODE"]]
        .astype(str)
        .apply(lambda s: s.str.strip())
        .drop_duplicates()
        .reset_index(drop=True)
    )
    cb("Đang lấy TRANSHDR đại diện đơn…")
    headers = fetch_transhdr_for_keys(date_start, date_end, bill_keys, progress=progress)

    if headers is not None and not headers.empty:
        orders = headers.copy()
    else:
        orders = lines.groupby(["STK_ID", "TRANS_NUM"], as_index=False).agg(
            TRAN_DATE=("TRAN_DATE", "first"),
            TRAN_TIME=("TRAN_TIME", "first"),
            CARD_ID=("CARD_ID", "first"),
            TRANS_CODE=("TRANS_CODE", "first"),
            bill_value=("line_total", "sum"),
        )
        cb("Cảnh báo: không khớp TRANSHDR — bill_value tạm = tổng dòng SP seed trên STRANS")

    return _apply_order_post_filters(
        orders,
        date_end=date_end,
        min_bill=min_bill,
        max_bill=max_bill,
        min_age=min_age,
        max_age=max_age,
        sex=sex,
        birth_month=birth_month,
        card_prefix=card_prefix,
        search=search,
        progress=progress,
    )


def _orders_for_skus(
    date_start: date,
    date_end: date,
    sku_ids: list[str],
    *,
    store_ids: list[str] | None,
    require_card: bool,
    min_bill: float | None,
    max_bill: float | None,
    gift_mode: GiftMode,
    progress: ProgressCb | None,
    min_age: float | None = None,
    max_age: float | None = None,
    sex: SexFilter = "any",
    birth_month: int | None = None,
    card_prefix: str = "",
    search: SearchOpts = DEFAULT_SEARCH,
) -> pd.DataFrame:
    """
    Return TRANSHDR rows (one per bill) for bills that contain any seed SKU on STRANS.
    Empty ``sku_ids`` → all bills via TRANSHDR (or DISTINCT STRANS keys when STK/gift).
    """
    cust_on = customer_filters_active(
        min_age=min_age,
        max_age=max_age,
        sex=sex,
        birth_month=birth_month,
        card_prefix=card_prefix,
    )
    if cust_on:
        require_card = True

    if not sku_ids:
        return _orders_all_in_period(
            date_start,
            date_end,
            store_ids=store_ids,
            require_card=require_card,
            min_bill=min_bill,
            max_bill=max_bill,
            gift_mode=gift_mode,
            progress=progress,
            min_age=min_age,
            max_age=max_age,
            sex=sex,
            birth_month=birth_month,
            card_prefix=card_prefix,
            search=search,
        )

    lines = _seed_lines_for_skus(
        date_start,
        date_end,
        sku_ids,
        store_ids=store_ids,
        require_card=require_card,
        gift_mode=gift_mode,
        card_prefix=card_prefix,
        search=search,
        progress=progress,
    )
    return _orders_from_seed_lines(
        date_start,
        date_end,
        lines,
        min_bill=min_bill,
        max_bill=max_bill,
        min_age=min_age,
        max_age=max_age,
        sex=sex,
        birth_month=birth_month,
        card_prefix=card_prefix,
        search=search,
        progress=progress,
    )


def fetch_product_orders(
    date_start: date,
    date_end: date,
    tokens: list[str],
    *,
    store_ids: list[str] | None = None,
    require_card: bool = True,
    min_bill: float | None = None,
    max_bill: float | None = None,
    gift_mode: GiftMode = "any",
    min_age: float | None = None,
    max_age: float | None = None,
    sex: SexFilter = "any",
    birth_month: int | None = None,
    card_prefix: str = "",
    search: SearchOpts = DEFAULT_SEARCH,
    progress: ProgressCb | None = None,
) -> tuple[dict[str, pd.DataFrame], list[str], dict[str, list[str]]]:
    """
    Returns (token -> TRANSHDR orders, unresolved_tokens, token -> seed SKU_IDs).

    Empty ``tokens`` → one bucket ``ALL_PRODUCTS_LABEL`` for every bill in A–B.
    Multiple tokens share a single STRANS seed pull.
    """
    cb = progress or (lambda _: None)
    cleaned = [str(t).strip() for t in (tokens or []) if t is not None and str(t).strip()]
    if not cleaned:
        cb("Danh sách SP trống — lấy tất cả đơn trong khoảng ngày…")
        orders = _orders_for_skus(
            date_start,
            date_end,
            [],
            store_ids=store_ids,
            require_card=require_card,
            min_bill=min_bill,
            max_bill=max_bill,
            gift_mode=gift_mode,
            progress=progress,
            min_age=min_age,
            max_age=max_age,
            sex=sex,
            birth_month=birth_month,
            card_prefix=card_prefix,
            search=search,
        )
        return {ALL_PRODUCTS_LABEL: orders}, [], {ALL_PRODUCTS_LABEL: []}

    cb("Đang resolve mã/tên mặt hàng…")
    resolved = resolve_product_tokens(cleaned, search=search)
    unresolved = [t for t, df in resolved.items() if df.empty]
    per_token: dict[str, pd.DataFrame] = {}
    seed_skus: dict[str, list[str]] = {}

    cust_on = customer_filters_active(
        min_age=min_age,
        max_age=max_age,
        sex=sex,
        birth_month=birth_month,
        card_prefix=card_prefix,
    )
    req_card = True if cust_on else require_card

    # One STRANS seed for all resolved SKUs, then split bills per token.
    all_skus: list[str] = []
    seen_sku: set[str] = set()
    for token, sku_df in resolved.items():
        if sku_df.empty:
            per_token[token] = pd.DataFrame(columns=ORDER_COLUMNS)
            seed_skus[token] = []
            continue
        ids = sku_df["SKU_ID"].astype(str).str.strip().tolist()
        seed_skus[token] = ids
        for sid in ids:
            if sid not in seen_sku:
                seen_sku.add(sid)
                all_skus.append(sid)

    if not all_skus:
        return per_token, unresolved, seed_skus

    lines = _seed_lines_for_skus(
        date_start,
        date_end,
        all_skus,
        store_ids=store_ids,
        require_card=req_card,
        gift_mode=gift_mode,
        card_prefix=card_prefix,
        search=search,
        progress=progress,
    )
    if lines is None or lines.empty:
        for token, ids in seed_skus.items():
            if ids:
                per_token[token] = pd.DataFrame(columns=ORDER_COLUMNS)
        return per_token, unresolved, seed_skus

    lines = lines.copy()
    lines["SKU_ID"] = lines["SKU_ID"].astype(str).str.strip()

    # One TRANSHDR rematch for all discovered bills, then slice per token.
    all_bill_keys = (
        lines[["STK_ID", "TRANS_NUM", "TRANS_CODE"]]
        .astype(str)
        .apply(lambda s: s.str.strip())
        .drop_duplicates()
        .reset_index(drop=True)
    )
    cb(f"Đang lấy TRANSHDR đại diện đơn ({len(all_bill_keys)} khóa)…")
    headers = fetch_transhdr_for_keys(
        date_start, date_end, all_bill_keys, progress=progress
    )

    for token, ids in seed_skus.items():
        if not ids:
            continue
        id_set = set(ids)
        tok_lines = lines.loc[lines["SKU_ID"].isin(id_set)]
        cb(f"Đơn chứa SP token={token!r} ({len(ids)} SKU)…")
        if tok_lines.empty:
            per_token[token] = pd.DataFrame(columns=ORDER_COLUMNS)
            continue
        tok_keys = (
            tok_lines[["STK_ID", "TRANS_NUM"]]
            .astype(str)
            .apply(lambda s: s.str.strip())
            .drop_duplicates()
        )
        if headers is not None and not headers.empty:
            orders = headers.merge(tok_keys, on=["STK_ID", "TRANS_NUM"], how="inner")
        else:
            orders = tok_lines.groupby(["STK_ID", "TRANS_NUM"], as_index=False).agg(
                TRAN_DATE=("TRAN_DATE", "first"),
                TRAN_TIME=("TRAN_TIME", "first"),
                CARD_ID=("CARD_ID", "first"),
                TRANS_CODE=("TRANS_CODE", "first"),
                bill_value=("line_total", "sum"),
            )
        per_token[token] = _apply_order_post_filters(
            orders,
            date_end=date_end,
            min_bill=min_bill,
            max_bill=max_bill,
            min_age=min_age,
            max_age=max_age,
            sex=sex,
            birth_month=birth_month,
            card_prefix=card_prefix,
            search=search,
            progress=progress,
        )
    return per_token, unresolved, seed_skus


def unique_card_customers(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty or "CARD_ID" not in df.columns:
        return pd.DataFrame(columns=CUSTOMER_COLUMNS)
    cards = (
        df["CARD_ID"].dropna().astype(str).str.strip().replace("", pd.NA).dropna().unique().tolist()
    )
    return lookup_cards(cards)


def _write_order_workbook(
    orders: pd.DataFrame,
    bill_lines: pd.DataFrame,
    path: Path,
) -> Path:
    """Main result: both modes — orders (TRANSHDR) + bill_lines (full STRANS)."""
    return write_excel_multi(
        {
            "orders": project_columns(orders, ORDER_COLUMNS),
            "bill_lines": project_columns(bill_lines, F5_ORDER_LINE_COLUMNS),
        },
        path,
    )


def _write_split_workbook(bill_lines: pd.DataFrame, path: Path) -> Path:
    """Split files always use mode 2 (full STRANS bill lines) only."""
    return write_excel(
        project_columns(bill_lines, F5_ORDER_LINE_COLUMNS),
        path,
        sheet_name="bill_lines",
    )


def export_product_orders(
    per_token: dict[str, pd.DataFrame],
    out_dir: Path,
    *,
    date_start: date,
    date_end: date,
    seed_skus_by_token: dict[str, list[str]] | None = None,
    include_aggregate: bool = True,
    include_card_list: bool = False,
    split_by: str | None = None,
    meta: dict[str, str] | None = None,
    sort_column: str | None = "TRANS_NUM",
    sort_ascending: bool = True,
    progress: ProgressCb | None = None,
    full_by_token: dict[str, pd.DataFrame] | None = None,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    cb = progress or (lambda _: None)
    seeds = seed_skus_by_token or {}
    cached_full = full_by_token or {}
    frames_ok: list[pd.DataFrame] = []
    full_ok: list[pd.DataFrame] = []
    all_seed: list[str] = []

    def _sorted(frame: pd.DataFrame) -> pd.DataFrame:
        return lead_and_sort(
            frame,
            lead="TRANS_NUM",
            column=sort_column,
            ascending=sort_ascending,
        )

    split_col = (split_by or "").strip() or None
    if split_col in ("", "none"):
        split_col = None

    for token, df in per_token.items():
        safe = sanitize_filename(token) or "token"
        orders = _sorted(project_columns(df, ORDER_COLUMNS))
        cached = cached_full.get(token)
        if cached is not None and not cached.empty:
            cb(f"Dùng cache full STRANS token={token!r}…")
            full = _sorted(cached)
        else:
            keys = bill_keys_from_lines(orders)
            cb(f"Bung full STRANS token={token!r} ({len(keys)} đơn)…")
            full = _sorted(fetch_bill_lines(date_start, date_end, keys, progress=progress))
        path = out_dir / f"don_chua_SP__{safe}.xlsx"
        _write_order_workbook(orders, full, path)
        written.append(path)

        excl = seeds.get(token) or []
        all_seed.extend(excl)
        report = build_orders_rich_report(
            title=f"Đơn chứa SP — {token}",
            matched_lines=orders,
            bill_lines=full,
            meta=meta,
            exclude_skus=excl,
            exclude_label="SKU đang tìm",
            include_per_bill_detail=True,
            per_card_limit=None,
        )
        rpath = out_dir / f"don_chua_SP__{safe}_report.txt"
        write_rich_lines(rpath, report)
        written.append(rpath)

        if orders is not None and not orders.empty:
            frames_ok.append(orders)
        if full is not None and not full.empty:
            full_ok.append(full)

        if split_col and full is not None and not full.empty and split_col in full.columns:
            parts = split_by_column(full, split_col)
            split_dir = out_dir / f"split_{safe}_by_{split_col}"
            for key, part_full in parts.items():
                p = split_dir / f"{sanitize_filename(key)}.xlsx"
                _write_split_workbook(_sorted(part_full), p)
                written.append(p)

    if include_aggregate and len(per_token) > 1 and frames_ok:
        agg = _sorted(
            pd.concat(frames_ok, ignore_index=True).drop_duplicates(
                subset=["STK_ID", "TRANS_NUM"], keep="first"
            )
        )
        agg_full = _sorted(
            pd.concat(full_ok, ignore_index=True).drop_duplicates(
                subset=["STK_ID", "TRANS_NUM", "SKU_ID"], keep="first"
            )
            if full_ok
            else pd.DataFrame(columns=F5_ORDER_LINE_COLUMNS)
        )
        agg_path = out_dir / "don_chua_SP__TONG.xlsx"
        _write_order_workbook(agg, agg_full, agg_path)
        written.append(agg_path)
        report = build_orders_rich_report(
            title="Đơn chứa SP — TỔNG",
            matched_lines=agg,
            bill_lines=agg_full,
            meta=meta,
            exclude_skus=sorted(set(all_seed)),
            exclude_label="SKU đang tìm",
            include_per_bill_detail=True,
            per_card_limit=None,
        )
        rpath = out_dir / "don_chua_SP__TONG_report.txt"
        write_rich_lines(rpath, report)
        written.append(rpath)

        if split_col and not agg_full.empty and split_col in agg_full.columns:
            parts = split_by_column(agg_full, split_col)
            split_dir = out_dir / f"split_TONG_by_{split_col}"
            for key, part_full in parts.items():
                p = split_dir / f"{sanitize_filename(key)}.xlsx"
                _write_split_workbook(_sorted(part_full), p)
                written.append(p)

        if include_card_list:
            cards = unique_card_customers(agg)
            cpath = out_dir / "khach_co_the_mua_SP.xlsx"
            write_excel(project_columns(cards, CUSTOMER_COLUMNS), cpath, sheet_name="cards")
            written.append(cpath)
    elif include_card_list and frames_ok:
        cards = unique_card_customers(pd.concat(frames_ok, ignore_index=True))
        cpath = out_dir / "khach_co_the_mua_SP.xlsx"
        write_excel(project_columns(cards, CUSTOMER_COLUMNS), cpath, sheet_name="cards")
        written.append(cpath)

    return written
