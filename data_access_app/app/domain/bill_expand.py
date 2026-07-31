"""Expand matched (STK_ID, TRANS_NUM) keys → full STRANS bill lines / TRANSHDR headers."""
from __future__ import annotations

from datetime import date
from typing import Callable

import pandas as pd

from app.db.dual_query import master_select, query_strans, query_transhdr
from app.domain.columns import BILL_VALUE_SQL, ORDER_COLUMNS, ORDER_LINE_COLUMNS
from app.domain.customer import lookup_cards
from app.export.excel import project_columns

ProgressCb = Callable[[str], None]

# Pair OR-clause chunk size (2 params each)
_KEY_CHUNK = 40
_TRANS_NUM_CHUNK = 80


def bill_keys_from_lines(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=["STK_ID", "TRANS_NUM"])
    return (
        df[["STK_ID", "TRANS_NUM"]]
        .dropna()
        .astype(str)
        .apply(lambda s: s.str.strip())
        .drop_duplicates()
        .reset_index(drop=True)
    )


def fetch_transhdr_for_keys(
    date_start: date,
    date_end: date,
    bill_keys: pd.DataFrame,
    *,
    progress: ProgressCb | None = None,
) -> pd.DataFrame:
    """
    Load TRANSHDR rows for discovered bills.

    Important: live TRANSHDR often has **blank STK_ID** while STRANS has the store.
    Never filter TRANSHDR by STK_ID chips — look up by TRANS_NUM (+ TRANS_CODE when present),
    then re-attach STK_ID from the STRANS-side keys.
    """
    cb = progress or (lambda _: None)
    if bill_keys is None or bill_keys.empty or "TRANS_NUM" not in bill_keys.columns:
        return pd.DataFrame(columns=ORDER_COLUMNS)

    keys = bill_keys.copy()
    keys["TRANS_NUM"] = keys["TRANS_NUM"].astype(str).str.strip()
    if "STK_ID" in keys.columns:
        keys["STK_ID"] = keys["STK_ID"].astype(str).str.strip()
    else:
        keys["STK_ID"] = ""
    has_code = "TRANS_CODE" in keys.columns
    if has_code:
        keys["TRANS_CODE"] = keys["TRANS_CODE"].astype(str).str.strip()

    key_cols = ["STK_ID", "TRANS_NUM"] + (["TRANS_CODE"] if has_code else [])
    keys = keys[key_cols].drop_duplicates().reset_index(drop=True)

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

    trans_nums = keys["TRANS_NUM"].dropna().astype(str).str.strip().unique().tolist()
    frames: list[pd.DataFrame] = []
    total = (len(trans_nums) + _TRANS_NUM_CHUNK - 1) // _TRANS_NUM_CHUNK
    for i in range(0, len(trans_nums), _TRANS_NUM_CHUNK):
        chunk = trans_nums[i : i + _TRANS_NUM_CHUNK]
        cb(f"Đang lấy TRANSHDR… chunk {i // _TRANS_NUM_CHUNK + 1}/{total} ({len(chunk)} TRANS_NUM)")
        ph = ",".join("?" for _ in chunk)
        part = query_transhdr(
            date_start,
            date_end,
            hdr_body,
            extra_where=f"LTRIM(RTRIM(TRANS_NUM)) IN ({ph})",
            extra_params=list(chunk),
            progress=None,
        )
        if part is not None and not part.empty:
            frames.append(part)

    if not frames:
        return pd.DataFrame(columns=ORDER_COLUMNS)

    hdr = pd.concat(frames, ignore_index=True)
    hdr["TRANS_NUM"] = hdr["TRANS_NUM"].astype(str).str.strip()
    if "TRANS_CODE" in hdr.columns:
        hdr["TRANS_CODE"] = hdr["TRANS_CODE"].astype(str).str.strip()
    hdr["bill_value"] = pd.to_numeric(hdr.get("bill_value"), errors="coerce").fillna(0.0)

    if has_code and "TRANS_CODE" in hdr.columns:
        merged = keys.merge(hdr, on=["TRANS_NUM", "TRANS_CODE"], how="inner", suffixes=("_k", ""))
        # STK_ID from keys (STRANS); HDR may be blank
        if "STK_ID_k" in merged.columns:
            merged["STK_ID"] = merged["STK_ID_k"]
            merged = merged.drop(columns=["STK_ID_k"])
    else:
        merged = keys.merge(hdr, on=["TRANS_NUM"], how="inner", suffixes=("_k", ""))
        if "STK_ID_k" in merged.columns:
            merged["STK_ID"] = merged["STK_ID_k"]
            merged = merged.drop(columns=["STK_ID_k"])
        if "TRANS_CODE_k" in merged.columns and "TRANS_CODE" not in merged.columns:
            merged = merged.rename(columns={"TRANS_CODE_k": "TRANS_CODE"})

    if merged.empty:
        return pd.DataFrame(columns=ORDER_COLUMNS)

    # If HDR.STK_ID was blank we already prefer keys; ensure column exists
    if "STK_ID" not in merged.columns:
        merged["STK_ID"] = keys["STK_ID"]

    keep = [
        "STK_ID",
        "TRANS_NUM",
        "TRAN_DATE",
        "TRAN_TIME",
        "CARD_ID",
        "TRANS_CODE",
        "bill_value",
    ]
    for c in keep:
        if c not in merged.columns:
            merged[c] = "" if c != "bill_value" else 0.0
    out = merged[keep].drop_duplicates(subset=["STK_ID", "TRANS_NUM"], keep="first")
    return out.reset_index(drop=True)



def enrich_order_lines(df: pd.DataFrame, *, with_cards: bool = True) -> pd.DataFrame:
    """Attach SKU_CODE / FULL_NAME_U and optional CARD NAME_U."""
    if df is None or df.empty:
        return pd.DataFrame(columns=ORDER_LINE_COLUMNS)
    kept = df.copy()
    sku_list = kept["SKU_ID"].dropna().astype(str).str.strip().unique().tolist()
    if sku_list:
        frames: list[pd.DataFrame] = []
        for i in range(0, len(sku_list), 400):
            chunk = sku_list[i : i + 400]
            ph = ",".join("?" for _ in chunk)
            frames.append(
                master_select(
                    f"SELECT SKU_ID, SKU_CODE, FULL_NAME_U FROM SKU_DEF WHERE SKU_ID IN ({ph})",
                    chunk,
                )
            )
        sku_df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        if not sku_df.empty:
            drop_cols = [c for c in ("SKU_CODE", "FULL_NAME_U") if c in kept.columns]
            if drop_cols:
                kept = kept.drop(columns=drop_cols)
            kept = kept.merge(sku_df, on="SKU_ID", how="left")

    if with_cards and "CARD_ID" in kept.columns:
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
            if not cdf.empty:
                name_col = "NAME" if "NAME" in cdf.columns else None
                cols = ["CARD_ID"]
                if "NAME_U" in cdf.columns:
                    cols.append("NAME_U")
                if name_col:
                    cols.append(name_col)
                drop_n = [c for c in ("NAME_U", "NAME") if c in kept.columns]
                if drop_n:
                    kept = kept.drop(columns=drop_n)
                kept = kept.merge(cdf[cols], on="CARD_ID", how="left")
                if "NAME_U" in kept.columns and "NAME" in kept.columns:
                    mask = kept["NAME_U"].isna() | (kept["NAME_U"].astype(str).str.strip() == "")
                    kept.loc[mask, "NAME_U"] = kept.loc[mask, "NAME"]
    return project_columns(kept, ORDER_LINE_COLUMNS)


def fetch_bill_lines(
    date_start: date,
    date_end: date,
    bill_keys: pd.DataFrame,
    *,
    progress: ProgressCb | None = None,
    with_cards: bool = True,
) -> pd.DataFrame:
    """
    Fetch every STRANS line for the given (STK_ID, TRANS_NUM) pairs.
    Value column: line_total = AMOUNT+SURPLUS+VAT (raw AMOUNT is not exported).
    """
    cb = progress or (lambda _: None)
    keys = bill_keys_from_lines(bill_keys)
    if keys.empty:
        return pd.DataFrame(columns=ORDER_LINE_COLUMNS)

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
            {BILL_VALUE_SQL} AS line_total
        FROM {{table}}
        WHERE 1=1
    """
    frames: list[pd.DataFrame] = []
    rows = list(keys.itertuples(index=False, name=None))
    total = (len(rows) + _KEY_CHUNK - 1) // _KEY_CHUNK
    for i in range(0, len(rows), _KEY_CHUNK):
        chunk = rows[i : i + _KEY_CHUNK]
        cb(f"Đang bung full bill… chunk {i // _KEY_CHUNK + 1}/{total} ({len(chunk)} đơn)")
        clauses = [
            "(LTRIM(RTRIM(STK_ID)) = ? AND LTRIM(RTRIM(TRANS_NUM)) = ?)" for _ in chunk
        ]
        params: list = []
        for stk, trans in chunk:
            params.extend([str(stk).strip(), str(trans).strip()])
        part = query_strans(
            date_start,
            date_end,
            body,
            extra_where=" OR ".join(clauses),
            extra_params=params,
            progress=None,
        )
        if part is not None and not part.empty:
            frames.append(part)

    if not frames:
        return pd.DataFrame(columns=ORDER_LINE_COLUMNS)
    raw = pd.concat(frames, ignore_index=True)
    raw["line_total"] = pd.to_numeric(raw.get("line_total"), errors="coerce").fillna(0.0)
    cb("Đang gắn tên SKU / thẻ cho full bill…")
    return enrich_order_lines(raw, with_cards=with_cards)


def fetch_card_period_lines(
    date_start: date,
    date_end: date,
    card_ids: list[str],
    *,
    store_ids: list[str] | None = None,
    progress: ProgressCb | None = None,
    with_cards: bool = True,
) -> pd.DataFrame:
    """All STRANS lines for a card cohort in A–B (F3 detail)."""
    cb = progress or (lambda _: None)
    cards = [c.strip() for c in card_ids if c and str(c).strip()]
    if not cards:
        return pd.DataFrame(columns=ORDER_LINE_COLUMNS)
    stores = [s.strip() for s in (store_ids or []) if s and str(s).strip()]
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
            {BILL_VALUE_SQL} AS line_total
        FROM {{table}}
        WHERE 1=1
    """
    frames: list[pd.DataFrame] = []
    for i in range(0, len(cards), 400):
        chunk = cards[i : i + 400]
        cb(f"Đang lấy dòng cohort… thẻ {i + 1}–{i + len(chunk)}/{len(cards)}")
        extra = [
            "CARD_ID IS NOT NULL",
            "LTRIM(RTRIM(CARD_ID)) <> ''",
            f"LTRIM(RTRIM(CARD_ID)) IN ({','.join('?' for _ in chunk)})",
        ]
        params: list = list(chunk)
        if stores:
            extra.append(f"LTRIM(RTRIM(STK_ID)) IN ({','.join('?' for _ in stores)})")
            params.extend(stores)
        part = query_strans(
            date_start,
            date_end,
            body,
            extra_where=" AND ".join(extra),
            extra_params=params,
            progress=None,
        )
        if part is not None and not part.empty:
            frames.append(part)
    if not frames:
        return pd.DataFrame(columns=ORDER_LINE_COLUMNS)
    raw = pd.concat(frames, ignore_index=True)
    raw["line_total"] = pd.to_numeric(raw.get("line_total"), errors="coerce").fillna(0.0)
    return enrich_order_lines(raw, with_cards=with_cards)
