"""Static table sample catalog for Agent II (offline JSON, no runtime SQL)."""

from __future__ import annotations

import json
import random
import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

from project_core.paths import ROOT
from project_core.text.tcvn3 import tcvn3_to_unicode

DEFAULT_SAMPLES_ROOT = ROOT / "data_dictionary" / "table_samples"
MAX_TABLES_PER_ATTEMPT = 6
ROWS_PER_TABLE = 5

_SHARD_RE = re.compile(
    r"^(?P<base>STRANS|PMTRANS|CRDTRANS|TRANSHDR)(?:_ARC)?(?:_\d{6})?$",
    re.IGNORECASE,
)

# Columns whose values must stay strings (leading zeros / padding matter).
_CODE_ID_HINTS = (
    "BARCODE",
    "SKU_CODE",
    "SKU_ID",
    "CARD_ID",
    "CUST_ID",
    "STK_ID",
    "TRANS_NUM",
    "TRANS_CODE",
    "PLU",
    "PLU_CODE",
)


def looks_like_code_or_id_column(name: str) -> bool:
    """True for ID/CODE-like columns that must not be stored as JSON numbers."""
    u = (name or "").strip().upper()
    if not u or u in {"SKU"}:  # SKU_DEF.SKU is a boolean flag, not an identifier
        return False
    if u in _CODE_ID_HINTS:
        return True
    if u.endswith(("_ID", "_CODE", "_NUM", "_SKU", "_PLU")):
        return True
    if u.endswith("CODE") or u.endswith("ID") or u.endswith("NUM"):
        return True
    if "BARCODE" in u:
        return True
    return False


def is_null_or_zero(value: Any) -> bool:
    """Null / numeric 0 / blank-or-whitespace-only string all count as empty."""
    if value is None:
        return True
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float, Decimal)):
        try:
            return float(value) == 0.0
        except (TypeError, ValueError):
            return False
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip() == ""
    return False


def sanitize_sample_value(column: str, value: Any) -> Any:
    """Normalize a cell for JSON samples: strip, TCVN3→Unicode, keep ID/CODE as strings."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value).strip()
    if isinstance(value, bytes):
        text = value.decode("utf-8", errors="replace").strip()
        return tcvn3_to_unicode(text) if text else text

    if looks_like_code_or_id_column(column):
        # Never persist identifier columns as JSON numbers (leading zeros would be lost).
        if isinstance(value, float) and value.is_integer():
            text = str(int(value))
        elif isinstance(value, int):
            text = str(value)
        else:
            text = str(value).strip()
        # Codes/IDs are usually ASCII digits; still run TCVN3 for safety on mixed fields.
        return tcvn3_to_unicode(text) if text else text

    if isinstance(value, str):
        text = value.strip()
        return tcvn3_to_unicode(text) if text else text
    if isinstance(value, (int, float)):
        return value
    text = str(value).strip()
    return tcvn3_to_unicode(text) if text else text


def sanitize_sample_row(row: dict[str, Any]) -> dict[str, Any]:
    return {str(k): sanitize_sample_value(str(k), v) for k, v in row.items()}


def row_null_or_zero_score(row: dict[str, Any]) -> int:
    """Score on sanitized values so whitespace-only cells count as empty."""
    return sum(1 for k, v in row.items() if is_null_or_zero(sanitize_sample_value(str(k), v)))


def pick_quality_rows(
    rows: list[dict[str, Any]],
    *,
    n: int = ROWS_PER_TABLE,
    rng: random.Random | None = None,
) -> list[dict[str, Any]]:
    """Prefer fewest null/zero/whitespace cells; fill up to n from best tiers.

    Returned rows are sanitized (strings stripped; ID/CODE forced to str).
    """
    if not rows or n <= 0:
        return []
    cleaned = [sanitize_sample_row(r) for r in rows if isinstance(r, dict)]
    chooser = rng or random.Random()
    scored = [(row_null_or_zero_score(r), i, r) for i, r in enumerate(cleaned)]
    by_score: dict[int, list[dict[str, Any]]] = {}
    for score, _i, row in scored:
        by_score.setdefault(score, []).append(row)
    picked: list[dict[str, Any]] = []
    for score in sorted(by_score):
        if len(picked) >= n:
            break
        tier = by_score[score]
        need = n - len(picked)
        if len(tier) <= need:
            picked.extend(tier)
        else:
            picked.extend(chooser.sample(tier, need))
    return picked


def normalize_sample_table_key(table: str) -> str:
    raw = (table or "").strip()
    if not raw:
        return ""
    name = raw.split(".")[-1]
    if name.upper().startswith("DBO."):
        name = name.split(".", 1)[-1]
    m = _SHARD_RE.match(name)
    if m:
        base = m.group("base").upper()
        if "ARC" in name.upper():
            return f"{base}_ARC" if base != "TRANSHDR" else "TRANSHDR_ARC"
        # db1 logical shards → STRANS / PMTRANS / CRDTRANS
        return base
    return name


def _preferred_data_sources(table: str, hint: str | None) -> list[str]:
    key = normalize_sample_table_key(table)
    upper = key.upper()
    if hint in {"db1", "db2"}:
        ordered = [hint] + [d for d in ("db2", "db1") if d != hint]
    elif upper in {"TRANSHDR_ARC", "CRDTRANS_ARC"} or upper.endswith("_ARC"):
        ordered = ["db1", "db2"]
    else:
        ordered = ["db2", "db1"]
    return ordered


def sample_path_for(table: str, data_source: str, *, root: Path | None = None) -> Path:
    base = root or DEFAULT_SAMPLES_ROOT
    key = normalize_sample_table_key(table)
    # Preserve documented casing when file exists; try exact then casefold scan
    direct = base / data_source / f"{key}.json"
    if direct.exists():
        return direct
    folder = base / data_source
    if folder.is_dir():
        for p in folder.glob("*.json"):
            if p.stem.lower() == key.lower():
                return p
    return direct


def load_one_table_sample(
    table: str,
    *,
    data_source_hint: str | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    key = normalize_sample_table_key(table)
    if not key:
        return {"table": table, "error": "sample_missing", "reason": "empty_table_name"}
    for ds in _preferred_data_sources(table, data_source_hint):
        path = sample_path_for(key, ds, root=root)
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {"table": key, "data_source": ds, "error": "sample_invalid", "reason": str(exc)[:200]}
        rows = payload.get("rows") or []
        columns = payload.get("columns") or (list(rows[0].keys()) if rows else [])
        return {
            "table": str(payload.get("table") or key),
            "data_source": str(payload.get("data_source") or ds),
            "columns": columns,
            "rows": rows[:ROWS_PER_TABLE],
            "row_count": min(len(rows), ROWS_PER_TABLE),
            "selection": payload.get("selection") or {},
            "requested_as": table,
        }
    return {"table": key, "error": "sample_missing", "requested_as": table}


def load_table_samples(
    tables: Iterable[str],
    *,
    allowed_tables: Iterable[str] | None = None,
    data_source_hints: dict[str, str] | None = None,
    target_dbs: list[str] | None = None,
    root: Path | None = None,
    max_tables: int = MAX_TABLES_PER_ATTEMPT,
) -> list[dict[str, Any]]:
    """Load up to max_tables static samples; ACL-filter when allowed_tables given."""
    allowed_upper: set[str] | None = None
    if allowed_tables is not None:
        allowed_upper = {str(t).split(".")[-1].upper() for t in allowed_tables}

    hints = data_source_hints or {}
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for idx, raw in enumerate(tables):
        if len(out) >= max_tables:
            break
        name = str(raw or "").strip()
        if not name:
            continue
        key = normalize_sample_table_key(name)
        if key.upper() in seen:
            continue
        if allowed_upper is not None and key.upper() not in allowed_upper:
            out.append(
                {
                    "table": key,
                    "requested_as": name,
                    "error": "table_not_allowed",
                }
            )
            seen.add(key.upper())
            continue
        hint = hints.get(name) or hints.get(key)
        if hint is None and target_dbs and idx < len(target_dbs):
            hint = target_dbs[idx]
        sample = load_one_table_sample(name, data_source_hint=hint, root=root)
        out.append(sample)
        seen.add(key.upper())
    return out
