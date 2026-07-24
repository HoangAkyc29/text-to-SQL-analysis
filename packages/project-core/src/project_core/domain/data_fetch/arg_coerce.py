"""Coerce / sanitize fetch args from LLM hints (reject prose placeholders)."""

from __future__ import annotations

import re
from typing import Any

from project_core.domain.data_fetch.flexible_builders import ALLOWED_FILTER_OPS

_OP_ALIASES = {
    ">=": "gte",
    "<=": "lte",
    ">": "gt",
    "<": "lt",
    "=": "eq",
    "==": "eq",
    "!=": "ne",
    "<>": "ne",
    "operator": "op",
}

_PROSE_HINT = re.compile(
    r"(?i)\b(from|brief|slice|dataset|available|hint|placeholder|time_range|filters?)\b"
)
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}")
_BRIEF_PATH = re.compile(
    r"(?i)^(brief(_slice)?|checklist|state|args_hints?)(\.|$)|"
    r"(^|\.)(time_range|filters|min_bill|product_code|codes)(\.|$)"
)


def looks_like_prose_placeholder(value: Any) -> bool:
    if value is None or isinstance(value, (bool, int, float)):
        return False
    if isinstance(value, list):
        return False
    if isinstance(value, dict):
        return False
    text = str(value).strip()
    if not text:
        return True
    if " " in text and _PROSE_HINT.search(text):
        return True
    if _BRIEF_PATH.search(text):
        return True
    if text.lower() in {
        "from brief",
        "from brief_slice",
        "brief.time_range",
        "brief_slice.time_range",
        "time_range from brief",
        "time_range from brief_slice",
    }:
        return True
    if text.startswith("{{") and text.endswith("}}"):
        return True
    # JSON-path style placeholders without spaces: brief_slice.filters.min_bill_value
    if "." in text and re.match(r"^[A-Za-z_][\w.]*$", text) and _PROSE_HINT.search(text.replace(".", " ")):
        return True
    return False


def coerce_time_range(
    value: Any, *, fallback: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Return a dict time_range; never pass strings into dict()."""
    if isinstance(value, dict):
        start = value.get("start")
        end = value.get("end")
        if start or end:
            out: dict[str, Any] = {}
            if start is not None and not looks_like_prose_placeholder(start):
                out["start"] = str(start)
            if end is not None and not looks_like_prose_placeholder(end):
                out["end"] = str(end)
            grain = value.get("grain")
            if grain is not None and not looks_like_prose_placeholder(grain):
                out["grain"] = grain
            if out.get("start") or out.get("end"):
                return out
    fb = fallback if isinstance(fallback, dict) else {}
    out = {}
    if fb.get("start"):
        out["start"] = str(fb["start"])
    if fb.get("end"):
        out["end"] = str(fb["end"])
    if fb.get("grain"):
        out["grain"] = fb["grain"]
    return out


def _normalize_op(raw: Any) -> str | None:
    text = str(raw or "eq").strip().lower()
    text = _OP_ALIASES.get(text, text)
    if text in ALLOWED_FILTER_OPS:
        return text
    return None


def sanitize_filter_clauses(filters: Any) -> list[dict[str, Any]]:
    """Keep only well-typed FilterClause dicts; drop prose values."""
    if not isinstance(filters, list):
        return []
    out: list[dict[str, Any]] = []
    for clause in filters:
        if not isinstance(clause, dict):
            continue
        col = clause.get("column") or clause.get("col")
        if not col or looks_like_prose_placeholder(col):
            continue
        op = _normalize_op(clause.get("op") or clause.get("operator"))
        if not op:
            continue
        item: dict[str, Any] = {"column": str(col).strip(), "op": op}
        if op in {"is_null", "is_not_null"}:
            out.append(item)
            continue
        value = clause.get("value")
        if looks_like_prose_placeholder(value):
            continue
        if isinstance(value, str) and " from " in value.lower():
            continue
        if op in {"in", "not_in"}:
            if isinstance(value, str) and not value.strip():
                continue
            # dataset ref string without spaces is OK (e.g. resolve_products)
            if isinstance(value, str) and (" " in value.strip() or not re.match(r"^[\w.\-]+$", value.strip())):
                if not re.match(r"^[\w]+$", value.strip()):
                    continue
        if op == "between":
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                continue
        item["value"] = value
        out.append(item)
    return out


def coerce_table_name(value: Any, *, fallback: str) -> str:
    if isinstance(value, str):
        name = value.strip().upper()
        if name and not looks_like_prose_placeholder(name) and re.match(r"^[A-Z][A-Z0-9_]*$", name):
            return name
    return str(fallback or "STRANS").strip().upper()


def coerce_dataset_ref(value: Any, *, known_refs: list[str] | None = None) -> Any:
    """Accept only concrete dataset names or id lists — not prose."""
    known = set(known_refs or [])
    if isinstance(value, list):
        ids = [str(x).strip() for x in value if str(x).strip() and not looks_like_prose_placeholder(x)]
        return ids or None
    if not isinstance(value, str):
        return None
    ref = value.strip()
    if not ref or looks_like_prose_placeholder(ref):
        return None
    if " " in ref:
        return None
    if known and ref not in known:
        # Still allow if it looks like a simple identifier; toolkit validates has()
        if not re.match(r"^[\w.\-]+$", ref):
            return None
    return ref


def coerce_product_codes(value: Any, *, fallback: list[str]) -> list[str]:
    if isinstance(value, list):
        codes = [
            str(x).strip()
            for x in value
            if str(x).strip() and not looks_like_prose_placeholder(x)
        ]
        if codes:
            return codes
    if isinstance(value, str) and value.strip() and not looks_like_prose_placeholder(value):
        if "," in value:
            return [p.strip() for p in value.split(",") if p.strip()]
        if " " not in value.strip():
            return [value.strip()]
    return list(fallback or [])
