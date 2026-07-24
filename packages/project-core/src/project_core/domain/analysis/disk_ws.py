"""Disk-backed working-set helpers for MCP stdio process boundaries."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd


def work_dir() -> Path:
    raw = os.getenv("DATA_AGENT_WORK_DIR") or ""
    path = Path(raw) if raw else Path("data/artifacts/_ws")
    path.mkdir(parents=True, exist_ok=True)
    return path


def out_dir() -> Path:
    raw = os.getenv("DATA_AGENT_OUT_DIR") or ""
    path = Path(raw) if raw else Path("data/artifacts/_out")
    path.mkdir(parents=True, exist_ok=True)
    return path


def frame_path(ref: str, *, root: Path | None = None) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in {"_", "-", "."} else "_" for ch in str(ref).strip())
    if not safe:
        raise ValueError("empty_dataset_ref")
    return (root or work_dir()) / f"{safe}.parquet"


def write_frame(ref: str, df: pd.DataFrame, *, root: Path | None = None) -> Path:
    path = frame_path(ref, root=root)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    meta = {
        "ref": ref,
        "row_count": int(len(df)),
        "columns": [str(c) for c in df.columns],
        "path": str(path),
    }
    path.with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    return path


def read_frame(ref: str, *, root: Path | None = None) -> pd.DataFrame:
    path = frame_path(ref, root=root)
    if not path.is_file():
        raise FileNotFoundError(f"unknown_dataset_ref:{ref}")
    return pd.read_parquet(path)


def list_dataset_profiles(*, root: Path | None = None) -> list[dict[str, Any]]:
    base = root or work_dir()
    out: list[dict[str, Any]] = []
    for meta_path in sorted(base.glob("*.meta.json")):
        try:
            body = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        out.append(body)
    return out


def sample_records(df: pd.DataFrame, n: int = 5) -> list[dict[str, Any]]:
    head = df.head(n).astype(object).where(pd.notnull(df.head(n)), None)
    return head.to_dict(orient="records")
