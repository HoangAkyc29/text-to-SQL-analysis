"""F3 — customers who purchased in A–B with points / value filters."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Callable, Literal

import pandas as pd

from app.db.dual_query import query_strans
from app.domain.bill_expand import fetch_card_period_lines
from app.domain.columns import BILL_VALUE_SQL, LOYALTY_METRIC_COLUMNS, ORDER_LINE_COLUMNS, POINTS_DIVISOR
from app.domain.customer import lookup_cards
from app.domain.search_opts import DEFAULT_SEARCH, SearchOpts, expand_prefix_params, match_prefix_column
from app.export.excel import project_columns, sanitize_filename, write_excel
from app.export.rich_report import build_loyalty_rich_report, write_rich_lines
from app.export.splitters import PointBucket, split_by_point_buckets

ProgressCb = Callable[[str], None]


def fetch_loyalty_customers(
    date_start: date,
    date_end: date,
    *,
    card_prefix: str = "",
    store_ids: list[str] | None = None,
    filter_mode: Literal["points", "value"] = "points",
    min_metric: float | None = None,
    max_metric: float | None = None,
    search: SearchOpts = DEFAULT_SEARCH,
    progress: ProgressCb | None = None,
) -> pd.DataFrame:
    cb = progress or (lambda _: None)
    stores = [s.strip() for s in (store_ids or []) if s and str(s).strip()]
    extra = ["CARD_ID IS NOT NULL", "LTRIM(RTRIM(CARD_ID)) <> ''"]
    params: list = []
    if stores:
        placeholders = ",".join("?" for _ in stores)
        extra.append(f"LTRIM(RTRIM(STK_ID)) IN ({placeholders})")
        params.extend(stores)
    if card_prefix.strip():
        extra.append(match_prefix_column("CARD_ID", search))
        params.extend(expand_prefix_params(card_prefix, 1, search))
    body = f"""
        SELECT
            LTRIM(RTRIM(CARD_ID)) AS CARD_ID,
            LTRIM(RTRIM(STK_ID)) AS STK_ID,
            LTRIM(RTRIM(TRANS_NUM)) AS TRANS_NUM,
            {BILL_VALUE_SQL} AS line_value
        FROM {{table}}
        WHERE 1=1
    """
    cb("Đang lấy dòng bán (dual db1/db2)…")
    lines = query_strans(
        date_start,
        date_end,
        body,
        extra_where=" AND ".join(extra),
        extra_params=params,
        progress=progress,
    )
    if lines.empty:
        return pd.DataFrame(columns=LOYALTY_METRIC_COLUMNS)

    lines["line_value"] = pd.to_numeric(lines["line_value"], errors="coerce").fillna(0.0)
    agg = (
        lines.groupby("CARD_ID", as_index=False)
        .agg(
            total_value=("line_value", "sum"),
            bill_count=("TRANS_NUM", "nunique"),
            STK_ID=("STK_ID", "min"),
        )
    )
    agg["points"] = agg["total_value"] / POINTS_DIVISOR

    metric_col = "points" if filter_mode == "points" else "total_value"
    if min_metric is not None:
        agg = agg.loc[agg[metric_col] >= float(min_metric)]
    if max_metric is not None:
        agg = agg.loc[agg[metric_col] <= float(max_metric)]

    cb("Đang gắn hồ sơ thẻ (CSCARD)…")
    cards = lookup_cards(agg["CARD_ID"].astype(str).tolist())
    if not cards.empty:
        merged = agg.merge(cards, on="CARD_ID", how="left", suffixes=("", "_c"))
    else:
        merged = agg
        for c in ("NAME_U", "PHONE", "MOBI", "SEX", "BIRTHDAY", "DISC_LVL"):
            if c not in merged.columns:
                merged[c] = None

    # Sort is applied in UI / export on final frames (not here).
    return project_columns(merged, LOYALTY_METRIC_COLUMNS)


def export_loyalty(
    df: pd.DataFrame,
    out_dir: Path,
    *,
    date_start: date,
    date_end: date,
    store_ids: list[str] | None = None,
    buckets: list[PointBucket] | None = None,
    txt_options: list[str] | None = None,
    meta: dict[str, str] | None = None,
    progress: ProgressCb | None = None,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    cb = progress or (lambda _: None)
    slim = project_columns(df, LOYALTY_METRIC_COLUMNS)

    if buckets:
        parts = split_by_point_buckets(slim, buckets, col="points")
        for label, part in parts.items():
            safe_label = sanitize_filename(label.replace(">=", "ge_").replace(">", "gt_"))
            path = out_dir / f"KH_mua_hang_diem_{safe_label}.xlsx"
            write_excel(part, path, sheet_name="customers")
            written.append(path)
    else:
        path = out_dir / "KH_mua_hang.xlsx"
        write_excel(slim, path, sheet_name="customers")
        written.append(path)

    card_ids = (
        slim["CARD_ID"].astype(str).str.strip().tolist()
        if slim is not None and not slim.empty and "CARD_ID" in slim.columns
        else []
    )
    cb(f"Đang lấy chi tiết giao dịch cohort ({len(card_ids)} thẻ)…")
    cohort_lines = fetch_card_period_lines(
        date_start,
        date_end,
        card_ids,
        store_ids=store_ids,
        progress=progress,
        with_cards=True,
    )
    detail_path = out_dir / "giao_dich_chi_tiet.xlsx"
    write_excel(
        project_columns(cohort_lines, ORDER_LINE_COLUMNS),
        detail_path,
        sheet_name="bill_lines",
    )
    written.append(detail_path)

    opts = txt_options or ["count", "by_points", "by_store", "by_age", "by_cycle", "by_hour"]
    report = build_loyalty_rich_report(
        customers=slim,
        cohort_lines=cohort_lines,
        meta=meta,
        options=opts,
    )
    txt_path = out_dir / "KH_mua_hang_report.txt"
    write_rich_lines(txt_path, report)
    written.append(txt_path)
    return written
