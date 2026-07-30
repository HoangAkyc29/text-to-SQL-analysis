"""F4 — orders for one or many customers in A–B."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Callable, Literal

import pandas as pd

from app.db.dual_query import query_strans, query_transhdr
from app.domain.bill_expand import bill_keys_from_lines, enrich_order_lines, fetch_bill_lines
from app.domain.columns import BILL_VALUE_SQL, F4_ORDER_LINE_COLUMNS, ORDER_COLUMNS
from app.domain.customer_filters import SexFilter, customer_filters_active, filter_frame_by_customer
from app.domain.product import search_products
from app.domain.search_opts import DEFAULT_SEARCH, SearchOpts, raise_if_truncated
from app.domain.frame_sort import lead_and_sort
from app.export.excel import (
    card_filename,
    customer_display_name,
    project_columns,
    write_excel,
    write_excel_multi,
)
from app.export.rich_report import build_orders_rich_report, write_rich_lines

ProgressCb = Callable[[str], None]
GiftMode = Literal["any", "paid", "gift"]


def _resolve_sku_ids(product_query: str, search: SearchOpts = DEFAULT_SEARCH) -> list[str]:
    q = (product_query or "").strip()
    if not q:
        return []
    df = search_products(code=q, search=search)
    df2 = search_products(name=q, search=search)
    raise_if_truncated(df, what=f"Mã SP {q!r}")
    raise_if_truncated(df2, what=f"Tên SP {q!r}")
    frames = [f for f in (df, df2) if not f.empty]
    if not frames:
        return []
    merged = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["SKU_ID"])
    return merged["SKU_ID"].astype(str).str.strip().tolist()


def fetch_customer_orders(
    date_start: date,
    date_end: date,
    card_ids: list[str],
    *,
    store_ids: list[str] | None = None,
    product_query: str = "",
    min_bill: float | None = None,
    max_bill: float | None = None,
    gift_mode: GiftMode = "any",
    min_age: float | None = None,
    max_age: float | None = None,
    sex: SexFilter = "any",
    search: SearchOpts = DEFAULT_SEARCH,
    progress: ProgressCb | None = None,
) -> tuple[pd.DataFrame, list[str]]:
    """
    Return (matched slim order-line frame, seed SKU_IDs if product filter else []).
    """
    cb = progress or (lambda _: None)
    cards = [c.strip() for c in card_ids if c and str(c).strip()]
    if not cards:
        raise ValueError("Cần ít nhất một mã thẻ")

    stores = [s.strip() for s in (store_ids or []) if s and str(s).strip()]
    sku_ids = _resolve_sku_ids(product_query, search) if product_query.strip() else []
    if product_query.strip() and not sku_ids:
        raise ValueError(f"Không tìm thấy mặt hàng khớp: {product_query}")
    extra = ["CARD_ID IS NOT NULL", "LTRIM(RTRIM(CARD_ID)) <> ''"]
    params: list = []
    placeholders = ",".join("?" for _ in cards)
    extra.append(f"LTRIM(RTRIM(CARD_ID)) IN ({placeholders})")
    params.extend(cards)
    if stores:
        ph = ",".join("?" for _ in stores)
        extra.append(f"LTRIM(RTRIM(STK_ID)) IN ({ph})")
        params.extend(stores)
    if sku_ids:
        ph = ",".join("?" for _ in sku_ids)
        extra.append(f"LTRIM(RTRIM(SKU_ID)) IN ({ph})")
        params.extend(sku_ids)
        if gift_mode == "paid":
            extra.append("ISNULL(AMOUNT,0) > 0")
        elif gift_mode == "gift":
            extra.append("ISNULL(AMOUNT,0) = 0")

    body = f"""
        SELECT
            LTRIM(RTRIM(STK_ID)) AS STK_ID,
            LTRIM(RTRIM(TRANS_NUM)) AS TRANS_NUM,
            TRAN_DATE,
            TRAN_TIME,
            LTRIM(RTRIM(CARD_ID)) AS CARD_ID,
            LTRIM(RTRIM(TRANS_CODE)) AS TRANS_CODE,
            IDX,
            LTRIM(RTRIM(SKU_ID)) AS SKU_ID,
            QTY,
            UNIT_SYMB,
            AMOUNT,
            {BILL_VALUE_SQL} AS line_value
        FROM {{table}}
        WHERE 1=1
    """
    cb("Đang lấy dòng bán theo thẻ…")
    lines = query_strans(
        date_start,
        date_end,
        body,
        extra_where=" AND ".join(extra),
        extra_params=params,
        progress=progress,
    )
    if lines.empty:
        return pd.DataFrame(columns=F4_ORDER_LINE_COLUMNS), sku_ids

    bill_keys = lines[["STK_ID", "TRANS_NUM"]].drop_duplicates()

    hdr_extra = []
    hdr_params: list = []
    # Không lọc TRANSHDR theo STK_ID — header thường để trống STK_ID; store đã lọc ở STRANS.
    hdr_extra.append(f"LTRIM(RTRIM(CARD_ID)) IN ({placeholders})")
    hdr_params.extend(cards)

    hdr_body = f"""
        SELECT
            LTRIM(RTRIM(STK_ID)) AS STK_ID,
            LTRIM(RTRIM(TRANS_NUM)) AS TRANS_NUM,
            TRAN_DATE,
            TRAN_TIME,
            LTRIM(RTRIM(CARD_ID)) AS CARD_ID,
            LTRIM(RTRIM(TRANS_CODE)) AS TRANS_CODE,
            {BILL_VALUE_SQL} AS bill_value
        FROM {{table}}
        WHERE 1=1
    """
    cb("Đang lấy header đơn…")
    headers = query_transhdr(
        date_start,
        date_end,
        hdr_body,
        extra_where=" AND ".join(hdr_extra) if hdr_extra else "",
        extra_params=hdr_params,
        progress=progress,
    )
    if headers.empty:
        bill_vals = (
            lines.groupby(["STK_ID", "TRANS_NUM"], as_index=False)
            .agg(
                bill_value=("line_value", "sum"),
                CARD_ID=("CARD_ID", "first"),
                TRAN_DATE=("TRAN_DATE", "first"),
                TRAN_TIME=("TRAN_TIME", "first"),
                TRANS_CODE=("TRANS_CODE", "first"),
            )
        )
    else:
        bill_vals = headers.drop_duplicates(subset=["STK_ID", "TRANS_NUM"])

    bill_vals["bill_value"] = pd.to_numeric(bill_vals["bill_value"], errors="coerce").fillna(0.0)
    if min_bill is not None:
        bill_vals = bill_vals.loc[bill_vals["bill_value"] >= float(min_bill)]
    if max_bill is not None:
        bill_vals = bill_vals.loc[bill_vals["bill_value"] <= float(max_bill)]

    bill_vals = bill_vals.merge(bill_keys, on=["STK_ID", "TRANS_NUM"], how="inner")
    kept = lines.merge(
        bill_vals[["STK_ID", "TRANS_NUM", "bill_value"]],
        on=["STK_ID", "TRANS_NUM"],
        how="inner",
    )
    kept = enrich_order_lines(kept, with_cards=True)

    if customer_filters_active(min_age=min_age, max_age=max_age, sex=sex):
        cb("Đang lọc theo tuổi / giới tính…")
        kept = filter_frame_by_customer(
            kept,
            min_age=min_age,
            max_age=max_age,
            sex=sex,
            as_of=date_end,
            search=search,
        )

    # Sort is applied in UI / export on final frames (not here).
    return project_columns(kept, F4_ORDER_LINE_COLUMNS), sku_ids


def export_customer_orders(
    df: pd.DataFrame,
    out_dir: Path,
    *,
    date_start: date,
    date_end: date,
    exclude_skus: list[str] | None = None,
    meta: dict[str, str] | None = None,
    sort_column: str | None = "TRANS_NUM",
    sort_ascending: bool = True,
    progress: ProgressCb | None = None,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    cb = progress or (lambda _: None)
    excl = exclude_skus or []

    def _sorted(frame: pd.DataFrame) -> pd.DataFrame:
        return lead_and_sort(
            frame,
            lead="TRANS_NUM",
            column=sort_column,
            ascending=sort_ascending,
        )

    if df is None or df.empty:
        p = out_dir / "don_hang_khach_EMPTY.xlsx"
        write_excel(pd.DataFrame(columns=F4_ORDER_LINE_COLUMNS), p)
        written.append(p)
        return written

    df = _sorted(df)

    # Expand once for all cards
    keys = bill_keys_from_lines(df)
    cb(f"Bung full bill ({len(keys)} đơn)…")
    all_full = _sorted(fetch_bill_lines(date_start, date_end, keys, progress=progress))

    # Aggregate report across all cards
    agg_report = build_orders_rich_report(
        title="Báo cáo đơn hàng theo khách — TỔNG",
        matched_lines=df,
        bill_lines=all_full,
        meta=meta,
        exclude_skus=excl if excl else None,
        exclude_label="SKU lọc" if excl else "—",
        include_per_bill_detail=True,
    )
    agg_txt = out_dir / "don_hang_khach_TONG_report.txt"
    write_rich_lines(agg_txt, agg_report)
    written.append(agg_txt)

    for card_id, group in df.groupby("CARD_ID"):
        name = customer_display_name(group.iloc[0])
        fname = card_filename(str(card_id), name) + ".xlsx"
        orders = _sorted(
            project_columns(
                group.drop_duplicates(subset=["STK_ID", "TRANS_NUM"]),
                ORDER_COLUMNS,
            )
        )
        matched = _sorted(project_columns(group, F4_ORDER_LINE_COLUMNS))
        part_keys = bill_keys_from_lines(matched)
        full = _sorted(
            all_full.merge(part_keys, on=["STK_ID", "TRANS_NUM"], how="inner")
            if all_full is not None and not all_full.empty and not part_keys.empty
            else pd.DataFrame(columns=F4_ORDER_LINE_COLUMNS)
        )
        # When no product filter, matched ≈ full already; still write both sheets.
        path = out_dir / fname
        write_excel_multi(
            {
                "orders": orders,
                "matched_lines": matched,
                "bill_lines": project_columns(full, F4_ORDER_LINE_COLUMNS),
            },
            path,
        )
        written.append(path)

        report = build_orders_rich_report(
            title=f"Báo cáo đơn hàng — {card_id}",
            matched_lines=matched,
            bill_lines=full,
            meta=meta,
            exclude_skus=excl if excl else None,
            exclude_label="SKU lọc" if excl else "—",
            include_per_bill_detail=True,
            per_card_limit=None,
        )
        txt = out_dir / (card_filename(str(card_id), name) + "_report.txt")
        write_rich_lines(txt, report)
        written.append(txt)
    return written
