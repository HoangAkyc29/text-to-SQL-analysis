"""Rich TXT statistical reports (sample_thongke-level detail, app value formula)."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

from app.export.excel import write_txt
from app.export.txt_report import age_years

PER_CARD_TXT_LIMIT = 80


def _fmt_num(v: float) -> str:
    try:
        return f"{float(v):,.2f}"
    except (TypeError, ValueError):
        return "0.00"


def _header(title: str, meta: dict[str, str] | None = None) -> list[str]:
    lines = [
        "=" * 70,
        title,
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "Giá trị dòng = AMOUNT + SURPLUS + VAT_AMT (line_total)",
        "=" * 70,
    ]
    for k, v in (meta or {}).items():
        lines.append(f"{k}: {v}")
    lines.append("")
    return lines


def bill_totals(bill_lines: pd.DataFrame) -> pd.DataFrame:
    """One row per (STK_ID, TRANS_NUM) with bill_total = sum(line_total)."""
    empty_cols = ["STK_ID", "TRANS_NUM", "CARD_ID", "TRAN_DATE", "TRAN_TIME", "bill_total", "NAME_U"]
    if bill_lines is None or bill_lines.empty:
        return pd.DataFrame(columns=empty_cols)
    df = bill_lines.copy()
    df["line_total"] = pd.to_numeric(df.get("line_total"), errors="coerce").fillna(0.0)
    aggs: dict = {
        "bill_total": ("line_total", "sum"),
        "CARD_ID": ("CARD_ID", "first"),
        "TRAN_DATE": ("TRAN_DATE", "first"),
        "TRAN_TIME": ("TRAN_TIME", "first"),
    }
    if "NAME_U" in df.columns:
        aggs["NAME_U"] = ("NAME_U", "first")
    out = df.groupby(["STK_ID", "TRANS_NUM"], as_index=False).agg(**aggs)
    if "NAME_U" not in out.columns:
        out["NAME_U"] = ""
    return out


def store_summary_frame(bill_lines: pd.DataFrame) -> pd.DataFrame:
    bills = bill_totals(bill_lines)
    if bills.empty:
        return pd.DataFrame(columns=["STK_ID", "SO_GIAO_DICH", "TONG_GIA_TRI", "TB_GIA_TRI"])
    out = (
        bills.groupby("STK_ID", as_index=False)
        .agg(SO_GIAO_DICH=("TRANS_NUM", "nunique"), TONG_GIA_TRI=("bill_total", "sum"))
    )
    out["TB_GIA_TRI"] = out["TONG_GIA_TRI"] / out["SO_GIAO_DICH"].clip(lower=1)
    return out.sort_values("STK_ID")


def format_store_summary_table(summary: pd.DataFrame) -> list[str]:
    lines = [
        "#" * 70,
        "THỐNG KÊ THEO TỪNG SIÊU THỊ (STK_ID)",
        "#" * 70,
        "",
        "+--------+--------------+----------------+--------------+",
        "| STK_ID | SO_GIAO_DICH | TONG_GIA_TRI   | TB_GIA_TRI   |",
        "+--------+--------------+----------------+--------------+",
    ]
    if summary is None or summary.empty:
        lines.append("| (trống)|              |                |              |")
    else:
        for _, row in summary.iterrows():
            lines.append(
                f"| {str(row['STK_ID']):<6} | {int(row['SO_GIAO_DICH']):>12} | "
                f"{_fmt_num(row['TONG_GIA_TRI']):>14} | {_fmt_num(row['TB_GIA_TRI']):>12} |"
            )
        tot_so = int(summary["SO_GIAO_DICH"].sum())
        tot_val = float(summary["TONG_GIA_TRI"].sum())
        tb = tot_val / tot_so if tot_so else 0.0
        lines.append("+--------+--------------+----------------+--------------+")
        lines.append(
            f"| TỔNG   | {tot_so:>12} | {_fmt_num(tot_val):>14} | {_fmt_num(tb):>12} |"
        )
    lines.append("+--------+--------------+----------------+--------------+")
    lines.append("")
    lines.append("Trong đó:")
    lines.append("- SO_GIAO_DICH = số (STK_ID, TRANS_NUM) unique tại siêu thị")
    lines.append("- TONG_GIA_TRI = tổng line_total mọi dòng full bill tại siêu thị")
    lines.append("- TB_GIA_TRI   = TONG_GIA_TRI / SO_GIAO_DICH")
    lines.append("")
    return lines


def sku_frequency(
    bill_lines: pd.DataFrame,
    *,
    exclude_skus: Iterable[str] | None = None,
    stk_id: str | None = None,
) -> pd.DataFrame:
    if bill_lines is None or bill_lines.empty or "SKU_ID" not in bill_lines.columns:
        return pd.DataFrame(columns=["SKU_ID", "FULL_NAME_U", "SO_LAN"])
    df = bill_lines
    if stk_id is not None:
        df = df.loc[df["STK_ID"].astype(str) == str(stk_id)]
    excl = {str(s).strip() for s in (exclude_skus or []) if s and str(s).strip()}
    if excl:
        df = df.loc[~df["SKU_ID"].astype(str).str.strip().isin(excl)]
    if df.empty:
        return pd.DataFrame(columns=["SKU_ID", "FULL_NAME_U", "SO_LAN"])
    name_col = "FULL_NAME_U" if "FULL_NAME_U" in df.columns else None
    gcols = ["SKU_ID"] + ([name_col] if name_col else [])
    freq = (
        df.groupby(gcols, dropna=False, as_index=False)
        .size()
        .rename(columns={"size": "SO_LAN"})
        .sort_values(["SO_LAN", "SKU_ID"], ascending=[False, True])
    )
    if name_col is None:
        freq["FULL_NAME_U"] = ""
    return freq


def format_sku_frequency_table(
    freq: pd.DataFrame,
    *,
    title: str,
) -> list[str]:
    lines = [
        "-" * 70,
        title,
        f"Số SKU khác nhau: {len(freq)}",
        "-" * 70,
        "+-----+--------------+------------------------------------------+--------+",
        "| STT | SKU_ID       | FULL_NAME_U                              | SO_LAN |",
        "+-----+--------------+------------------------------------------+--------+",
    ]
    if freq is None or freq.empty:
        lines.append("|   — |              | (không có)                               |      — |")
    else:
        for i, row in enumerate(freq.itertuples(index=False), start=1):
            sku = str(getattr(row, "SKU_ID", "") or "")[:12]
            name = str(getattr(row, "FULL_NAME_U", "") or "(không có tên)")[:40]
            cnt = int(getattr(row, "SO_LAN", 0))
            lines.append(f"| {i:>3} | {sku:<12} | {name:<40} | {cnt:>6} |")
    lines.append("+-----+--------------+------------------------------------------+--------+")
    lines.append("")
    return lines


def format_line_items_table(lines_df: pd.DataFrame) -> list[str]:
    out = [
        "+-----+--------------+------------------------------------------+------------+",
        "| STT | SKU_ID       | FULL_NAME_U                              | line_total |",
        "+-----+--------------+------------------------------------------+------------+",
    ]
    if lines_df is None or lines_df.empty:
        out.append("|   — |              | (không có dòng)                          |          — |")
    else:
        view = lines_df.reset_index(drop=True)
        for i, row in view.iterrows():
            sku = str(row.get("SKU_ID", "") or "")[:12]
            name = str(row.get("FULL_NAME_U", "") or "(không có tên)")[:40]
            val = _fmt_num(row.get("line_total", 0))
            out.append(f"| {int(i) + 1:>3} | {sku:<12} | {name:<40} | {val:>10} |")
    out.append("+-----+--------------+------------------------------------------+------------+")
    return out


def format_bill_blocks(
    bill_lines: pd.DataFrame,
    *,
    stk_id: str | None = None,
    max_cards: int | None = None,
) -> list[str]:
    if bill_lines is None or bill_lines.empty:
        return ["(không có giao dịch)", ""]
    df = bill_lines
    if stk_id is not None:
        df = df.loc[df["STK_ID"].astype(str) == str(stk_id)]
    bills = bill_totals(df)
    if bills.empty:
        return ["(không có đơn)", ""]
    bills = bills.sort_values(["CARD_ID", "TRANS_NUM"])
    if max_cards is not None:
        cards = bills["CARD_ID"].astype(str).unique().tolist()
        if len(cards) > max_cards:
            return [
                f"(bỏ qua chi tiết từng thẻ — {len(cards)} thẻ > ngưỡng {max_cards}; xem Excel bill_lines)",
                "",
            ]

    out: list[str] = []
    for _, bill in bills.iterrows():
        card = str(bill.get("CARD_ID") or "")
        trans = str(bill.get("TRANS_NUM") or "")
        stk = str(bill.get("STK_ID") or "")
        total = float(bill.get("bill_total") or 0)
        name = ""
        if "NAME_U" in bill.index and pd.notna(bill.get("NAME_U")):
            name = str(bill.get("NAME_U"))
        elif "NAME_U" in df.columns:
            sub = df.loc[
                (df["STK_ID"].astype(str) == stk) & (df["TRANS_NUM"].astype(str) == trans)
            ]
            if not sub.empty and "NAME_U" in sub.columns:
                nv = sub["NAME_U"].dropna()
                if not nv.empty:
                    name = str(nv.iloc[0])

        out.append("=" * 50)
        out.append(f"          >>>  CARD_ID : {card}  <<<")
        out.append("=" * 50)
        if name:
            out.append(f"Tên khách hàng           : {name}")
        out.append(f"Mã giao dịch (TRANS_NUM) : {trans}")
        out.append(f"STK_ID                   : {stk}")
        out.append(f"Tổng giá trị đơn (sum line_total): {_fmt_num(total)}")
        out.append("Danh sách mặt hàng trong đơn (full STRANS):")
        item_df = df.loc[
            (df["STK_ID"].astype(str) == stk) & (df["TRANS_NUM"].astype(str) == trans)
        ].sort_values("IDX" if "IDX" in df.columns else "SKU_ID")
        out.extend(format_line_items_table(item_df))
        out.append("-" * 53)
        out.append("")
    return out


def _hour_month_sections(bill_lines: pd.DataFrame) -> list[str]:
    lines: list[str] = []
    bills = bill_totals(bill_lines)
    if bills.empty:
        return lines
    if "TRAN_TIME" in bills.columns:
        lines.append("[Theo giờ trong ngày — theo đơn]")
        hours = bills["TRAN_TIME"].astype(str).str.slice(0, 2)
        for h, cnt in hours.value_counts().sort_index().items():
            if h and h.lower() not in {"na", "nat", "none"}:
                lines.append(f"  {h}h: {cnt} đơn")
        lines.append("")
    if "TRAN_DATE" in bills.columns:
        lines.append("[Theo chu kỳ — tháng]")
        months = pd.to_datetime(bills["TRAN_DATE"], errors="coerce").dt.to_period("M")
        for m, cnt in months.value_counts().sort_index().items():
            lines.append(f"  {m}: {cnt} đơn")
        lines.append("")
    return lines


def build_orders_rich_report(
    *,
    title: str,
    matched_lines: pd.DataFrame | None,
    bill_lines: pd.DataFrame,
    meta: dict[str, str] | None = None,
    exclude_skus: Iterable[str] | None = None,
    exclude_label: str = "SKU seed",
    include_per_bill_detail: bool = True,
    per_card_limit: int | None = PER_CARD_TXT_LIMIT,
) -> list[str]:
    """Shared F4/F5 style: store summary + optional bill detail + SKU frequency."""
    lines = _header(title, meta)
    n_match = 0 if matched_lines is None or matched_lines.empty else len(matched_lines)
    n_full = 0 if bill_lines is None or bill_lines.empty else len(bill_lines)
    bills = bill_totals(bill_lines)
    # matched_lines may be TRANSHDR orders (F5) or seed STRANS lines (F4)
    lines.append(
        f"[Tóm tắt] orders/matched={n_match} · bill_lines={n_full} · số đơn={len(bills)}"
    )
    if not bills.empty:
        lines.append(f"  Tổng giá trị (sum bill từ STRANS): {_fmt_num(bills['bill_total'].sum())}")
        lines.append(f"  TB / đơn: {_fmt_num(bills['bill_total'].mean())}")
    lines.append("")

    summary = store_summary_frame(bill_lines)
    lines.extend(format_store_summary_table(summary))

    if include_per_bill_detail and not summary.empty:
        for stk in summary["STK_ID"].astype(str).tolist():
            sub_bills = bills.loc[bills["STK_ID"].astype(str) == stk]
            lines.append("#" * 70)
            lines.append(f"NHÓM STK_ID = {stk}")
            lines.append(f"Số đơn (unique TRANS_NUM): {len(sub_bills)}")
            lines.append(f"Tổng giá trị: {_fmt_num(sub_bills['bill_total'].sum())}")
            tb = float(sub_bills["bill_total"].mean()) if len(sub_bills) else 0.0
            lines.append(f"Trung bình / đơn: {_fmt_num(tb)}")
            lines.append("#" * 70)
            lines.append("")
            lines.extend(
                format_bill_blocks(
                    bill_lines,
                    stk_id=stk,
                    max_cards=per_card_limit,
                )
            )
            excl = list(exclude_skus or [])
            freq_title = (
                f"TẦN SUẤT MẶT HÀNG TẠI STK_ID = {stk}"
                + (f" (loại trừ {exclude_label})" if excl else "")
            )
            lines.extend(
                format_sku_frequency_table(
                    sku_frequency(bill_lines, exclude_skus=excl, stk_id=stk),
                    title=freq_title,
                )
            )

    excl = list(exclude_skus or [])
    overall_title = (
        "TẦN SUẤT MẶT HÀNG TỔNG HỢP (TẤT CẢ SIÊU THỊ)"
        + (f" — loại trừ {exclude_label}" if excl else "")
    )
    lines.extend(
        format_sku_frequency_table(
            sku_frequency(bill_lines, exclude_skus=excl),
            title=overall_title,
        )
    )
    lines.extend(_hour_month_sections(bill_lines))

    lines.append("=" * 70)
    lines.append("TÓM TẮT")
    lines.append(f"- Số đơn: {len(bills)}")
    for _, row in summary.iterrows():
        lines.append(
            f"- STK {row['STK_ID']}: {int(row['SO_GIAO_DICH'])} đơn / "
            f"tổng {_fmt_num(row['TONG_GIA_TRI'])}"
        )
    lines.append("=" * 70)
    return lines


def build_loyalty_rich_report(
    *,
    customers: pd.DataFrame,
    cohort_lines: pd.DataFrame,
    meta: dict[str, str] | None = None,
    options: Iterable[str] | None = None,
    per_card_limit: int = PER_CARD_TXT_LIMIT,
) -> list[str]:
    """F3: cohort summary, store from real STRANS, points/age, top SKUs, optional per-card."""
    opts = set(options or ["count", "by_points", "by_store", "by_age", "by_cycle", "by_hour"])
    lines = _header("BÁO CÁO KHÁCH HÀNG THEO KỲ (F3)", meta)
    cust = customers if customers is not None else pd.DataFrame()
    n = len(cust)
    lines.append(f"[Cohort] số khách = {n}")
    if n and "total_value" in cust.columns:
        tv = pd.to_numeric(cust["total_value"], errors="coerce").fillna(0.0)
        lines.append(f"  Tổng giá trị: {_fmt_num(tv.sum())}")
        lines.append(f"  TB giá trị / KH: {_fmt_num(tv.mean())}")
    if n and "points" in cust.columns:
        pts = pd.to_numeric(cust["points"], errors="coerce").fillna(0.0)
        lines.append(f"  Tổng điểm: {_fmt_num(pts.sum())}")
        lines.append(f"  TB điểm / KH: {_fmt_num(pts.mean())}")
    lines.append("")

    if "by_store" in opts or "count" in opts:
        summary = store_summary_frame(cohort_lines)
        lines.extend(format_store_summary_table(summary))

    if "by_points" in opts and "points" in cust.columns and not cust.empty:
        lines.append("[Theo điểm — histogram]")
        s = pd.to_numeric(cust["points"], errors="coerce").dropna()
        if not s.empty:
            bins = [0, 50, 100, 200, 500, 1000, 5000, float("inf")]
            cats = pd.cut(s, bins=bins, right=False)
            for label, cnt in cats.value_counts().sort_index().items():
                lines.append(f"  {label}: {cnt}")
        lines.append("")

    if "by_age" in opts and "BIRTHDAY" in cust.columns and not cust.empty:
        lines.append("[Theo độ tuổi]")
        ages = cust["BIRTHDAY"].map(age_years).dropna()
        if ages.empty:
            lines.append("  (không có BIRTHDAY)")
        else:
            bins = [0, 18, 25, 35, 45, 55, 65, 120]
            cats = pd.cut(ages, bins=bins, right=False)
            for label, cnt in cats.value_counts().sort_index().items():
                lines.append(f"  {label}: {cnt}")
        lines.append("")

    lines.extend(
        format_sku_frequency_table(
            sku_frequency(cohort_lines),
            title="TOP MẶT HÀNG COHORT MUA TRONG KỲ (tất cả siêu thị)",
        )
    )

    if "by_hour" in opts or "by_cycle" in opts:
        lines.extend(_hour_month_sections(cohort_lines))

    n_cards = (
        cohort_lines["CARD_ID"].astype(str).nunique()
        if cohort_lines is not None and not cohort_lines.empty and "CARD_ID" in cohort_lines.columns
        else n
    )
    if n_cards <= per_card_limit:
        lines.append("#" * 70)
        lines.append("CHI TIẾT TỪNG THẺ (full dòng STRANS trong kỳ)")
        lines.append("#" * 70)
        lines.append("")
        # Group by store then cards
        summary = store_summary_frame(cohort_lines)
        for stk in summary["STK_ID"].astype(str).tolist() if not summary.empty else []:
            lines.append(f"--- STK_ID = {stk} ---")
            lines.extend(format_bill_blocks(cohort_lines, stk_id=stk, max_cards=None))
    else:
        lines.append(
            f"(Chi tiết từng thẻ bỏ qua trong TXT — {n_cards} thẻ > ngưỡng {per_card_limit}; "
            "xem Excel giao_dich_chi_tiet.xlsx / bill_lines)"
        )
        lines.append("")

    lines.append("=" * 70)
    lines.append("TÓM TẮT")
    lines.append(f"- Số khách cohort: {n}")
    summary = store_summary_frame(cohort_lines)
    for _, row in summary.iterrows():
        lines.append(
            f"- STK {row['STK_ID']}: {int(row['SO_GIAO_DICH'])} đơn / "
            f"tổng {_fmt_num(row['TONG_GIA_TRI'])}"
        )
    lines.append("=" * 70)
    return lines


def write_rich_lines(path: Path, lines: list[str]) -> Path:
    return write_txt(lines, path)
