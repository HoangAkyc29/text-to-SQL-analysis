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
from project_core.text.tcvn3 import is_unicode_text_column, tcvn3_to_unicode

DEFAULT_SAMPLES_ROOT = ROOT / "data_dictionary" / "table_samples"
MAX_TABLES_PER_ATTEMPT = 6
ROWS_PER_TABLE = 5

_SHARD_RE = re.compile(
    r"^(?P<base>STRANS|PMTRANS|CRDTRANS|TRANSHDR)(?:_ARC)?(?:_\d{6})?$",
    re.IGNORECASE,
)
# Only true physical month shards (not bare logical STRANS).
_SHARD_PHYSICAL_RE = re.compile(
    r"^(?P<base>STRANS|PMTRANS|CRDTRANS)_\d{6}$",
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
        if is_unicode_text_column(column):
            return text
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
        if is_unicode_text_column(column):
            return text
        return tcvn3_to_unicode(text) if text else text
    if isinstance(value, (int, float)):
        return value
    text = str(value).strip()
    if is_unicode_text_column(column):
        return text
    return tcvn3_to_unicode(text) if text else text


def sanitize_sample_row(row: dict[str, Any]) -> dict[str, Any]:
    return {str(k): sanitize_sample_value(str(k), v) for k, v in row.items()}


def row_null_or_zero_score(row: dict[str, Any]) -> int:
    """Score on sanitized values so whitespace-only cells count as empty."""
    return sum(1 for k, v in row.items() if is_null_or_zero(sanitize_sample_value(str(k), v)))


def _diversity_gain(candidate: dict[str, Any], picked: list[dict[str, Any]]) -> float:
    """Rarity-weighted count of new non-empty values vs picked set (higher = better).

    Columns that are still mono / empty in the picked set get a large boost when a
    new value appears — so e.g. a new TRANS_CODE beats another SKU_ID variant.
    """
    if not picked:
        return float(sum(1 for v in candidate.values() if not is_null_or_zero(v)))
    gain = 0.0
    for col, val in candidate.items():
        if is_null_or_zero(val):
            continue
        seen = {p.get(col) for p in picked if not is_null_or_zero(p.get(col))}
        if val in seen:
            continue
        # Prefer breaking mono columns first.
        if len(seen) <= 1:
            gain += 12.0
        else:
            gain += 1.0 / (1.0 + len(seen))
    return gain


def _overlap_count(candidate: dict[str, Any], picked: list[dict[str, Any]]) -> int:
    """Count non-empty cells matching any already-picked row on the same column (lower = better)."""
    if not picked:
        return 0
    overlaps = 0
    for col, val in candidate.items():
        if is_null_or_zero(val):
            continue
        if any(p.get(col) == val for p in picked):
            overlaps += 1
    return overlaps


def pick_quality_rows(
    rows: list[dict[str, Any]],
    *,
    n: int = ROWS_PER_TABLE,
    rng: random.Random | None = None,
) -> list[dict[str, Any]]:
    """Pick up to n sanitized rows: prefer dense rows, maximize value diversity.

    Uses the **full** candidate list (not only the densest tier) so categorical
    diversity (e.g. TRANS_CODE) is not wiped out by TOP-N skewed sources. Quality
    only biases the seed row toward denser examples.
    """
    if not rows or n <= 0:
        return []
    cleaned = [sanitize_sample_row(r) for r in rows if isinstance(r, dict)]
    chooser = rng or random.Random()

    # Drop exact duplicate rows.
    unique: list[tuple[int, dict[str, Any]]] = []
    seen_fp: set[str] = set()
    for idx, row in enumerate(cleaned):
        fp = json.dumps(row, sort_keys=True, default=str, ensure_ascii=False)
        if fp in seen_fp:
            continue
        seen_fp.add(fp)
        unique.append((idx, row))

    if len(unique) <= n:
        return [row for _, row in unique]

    scores = {idx: row_null_or_zero_score(row) for idx, row in unique}
    best_q = min(scores.values())
    # Seed among densest quartile (or best score), random among those.
    sorted_by_q = sorted(unique, key=lambda ir: scores[ir[0]])
    seed_cut = max(1, len(sorted_by_q) // 4)
    seed_pool = [(i, r) for i, r in sorted_by_q[:seed_cut] if scores[i] == best_q] or sorted_by_q[:seed_cut]
    seed_idx, seed_row = chooser.choice(seed_pool)
    picked: list[dict[str, Any]] = [seed_row]
    remaining = [(idx, row) for idx, row in unique if idx != seed_idx]

    while len(picked) < n and remaining:
        best_key: tuple[float, int, float] | None = None
        best_item: tuple[int, dict[str, Any]] | None = None
        for idx, row in remaining:
            # Maximize rarity-weighted new values; then minimize raw overlaps.
            gain = _diversity_gain(row, picked)
            overlaps = _overlap_count(row, picked)
            key = (-gain, overlaps, chooser.random())
            if best_key is None or key < best_key:
                best_key = key
                best_item = (idx, row)
        assert best_item is not None
        pick_idx, pick_row = best_item
        picked.append(pick_row)
        remaining = [(idx, row) for idx, row in remaining if idx != pick_idx]
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


_DB1_FACT_LOGICAL = frozenset({"STRANS", "PMTRANS", "CRDTRANS", "TRANSHDR_ARC", "CRDTRANS_ARC"})


def infer_sample_data_sources(
    table: str,
    *,
    hint: str | None = None,
    needs_db1: bool = False,
    needs_db2: bool = False,
) -> list[str]:
    """Decide which sample files to load for a logical/physical table name.

    - Explicit hint wins (single source).
    - ARC / db1-only history → db1.
    - Fact tables spanning cutoff (needs_db1+needs_db2) → both db2 then db1.
    - Otherwise prefer db2, fall back db1.
    """
    key = normalize_sample_table_key(table).upper()
    if hint in {"db1", "db2"}:
        return [hint]
    if key.endswith("_ARC") or key in {"TRANSHDR_ARC", "CRDTRANS_ARC"}:
        return ["db1"]
    # Physical month shard implies archive history on db1.
    if _SHARD_PHYSICAL_RE.match(table or ""):
        return ["db1"]
    if key in {"STRANS", "PMTRANS", "CRDTRANS"}:
        if needs_db1 and needs_db2:
            return ["db2", "db1"]
        if needs_db1 and not needs_db2:
            return ["db1"]
        return ["db2"]
    if needs_db1 and not needs_db2 and key in _DB1_FACT_LOGICAL:
        return ["db1"]
    return ["db2"]


def _preferred_data_sources(table: str, hint: str | None) -> list[str]:
    """Resolve which sample folders to try for one logical table.

    When ``hint`` is an explicit db1/db2 request (e.g. from
    ``infer_sample_data_sources`` / agent ``selected_target_dbs``), only that
    folder is tried — never silently fall back to the other DB. Cross-DB
    fallback is only for unhinted lookups.
    """
    key = normalize_sample_table_key(table)
    upper = key.upper()
    if hint in {"db1", "db2"}:
        return [hint]
    if upper in {"TRANSHDR_ARC", "CRDTRANS_ARC"} or upper.endswith("_ARC"):
        return ["db1", "db2"]
    return ["db2", "db1"]


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
    needs_db1: bool = False,
    needs_db2: bool = False,
    root: Path | None = None,
    max_tables: int = MAX_TABLES_PER_ATTEMPT,
) -> list[dict[str, Any]]:
    """Load up to max_tables static samples; ACL-filter when allowed_tables given.

    Same logical table may appear once per data_source (e.g. STRANS db2 + db1)
    when the date range spans the archive cutoff.
    """
    allowed_upper: set[str] | None = None
    if allowed_tables is not None:
        allowed_upper = {str(t).split(".")[-1].upper() for t in allowed_tables}

    hints = data_source_hints or {}
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for idx, raw in enumerate(tables):
        if len(out) >= max_tables:
            break
        name = str(raw or "").strip()
        if not name:
            continue
        key = normalize_sample_table_key(name)
        if allowed_upper is not None and key.upper() not in allowed_upper:
            out.append(
                {
                    "table": key,
                    "requested_as": name,
                    "error": "table_not_allowed",
                }
            )
            continue
        hint = hints.get(name) or hints.get(key)
        if hint is None and target_dbs and idx < len(target_dbs):
            hint = target_dbs[idx]
        sources = infer_sample_data_sources(
            name,
            hint=hint if hint in {"db1", "db2"} else None,
            needs_db1=needs_db1,
            needs_db2=needs_db2,
        )
        for ds in sources:
            if len(out) >= max_tables:
                break
            seen_key = (ds, key.upper())
            if seen_key in seen:
                continue
            sample = load_one_table_sample(name, data_source_hint=ds, root=root)
            out.append(sample)
            seen.add(seen_key)
    return out
