"""Excel + TXT export helpers."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd


def sanitize_filename(name: str, max_len: int = 120) -> str:
    cleaned = name.replace(">=", "ge_").replace("<=", "le_").replace(">", "gt_").replace("<", "lt_")
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", cleaned.strip())
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    if not cleaned:
        cleaned = "untitled"
    return cleaned[:max_len]


def write_excel(df: pd.DataFrame, path: Path, sheet_name: str = "data") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Excel sheet name max 31 chars
    safe_sheet = sanitize_filename(sheet_name, 31) or "data"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        (df if df is not None else pd.DataFrame()).to_excel(
            writer, index=False, sheet_name=safe_sheet
        )
    return path


def write_excel_multi(sheets: dict[str, pd.DataFrame], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            safe = sanitize_filename(name, 31) or "sheet"
            (df if df is not None else pd.DataFrame()).to_excel(
                writer, index=False, sheet_name=safe
            )
    return path


def write_txt(lines: list[str], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def project_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=columns)
    keep = [c for c in columns if c in df.columns]
    return df.loc[:, keep].copy()


def customer_display_name(row: dict[str, Any] | pd.Series) -> str:
    for key in ("NAME_U", "NAME", "CUST_NAME_U", "CUST_NAME"):
        val = row.get(key) if isinstance(row, dict) else row.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    return "Không có tên khách"


def card_filename(card_id: str, name: str) -> str:
    return sanitize_filename(f"{card_id} – {name}")
