"""Coerce / sanitize fetch args from LLM hints (reject prose placeholders)."""

from __future__ import annotations

import re
from datetime import date, datetime
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
_ISO_DATE_IN_TEXT = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
_VN_DATE_IN_TEXT = re.compile(r"\b(\d{1,2})[/.](\d{1,2})(?:[/.](\d{2,4}))?\b")
_NOW_END_TOKENS = re.compile(
    r"(?i)\b(hiện nay|den nay|đến nay|hom nay|hôm nay|today|now|present|hiện tại|hien tai)\b"
)
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


def _parse_vn_date_token(day: str, month: str, year_raw: str | None) -> str | None:
    today = date.today()
    try:
        d = int(day)
        m = int(month)
    except ValueError:
        return None
    if year_raw:
        y = int(year_raw)
        if y < 100:
            y += 2000
    else:
        y = today.year
    try:
        return date(y, m, d).isoformat()
    except ValueError:
        return None


def _extract_time_range_from_text(text: str) -> dict[str, Any]:
    """Best-effort date window from free-text clarify answers / intent."""
    prose = str(text or "").strip()
    if not prose:
        return {}
    out: dict[str, Any] = {}
    iso_hits = _ISO_DATE_IN_TEXT.findall(prose)
    if iso_hits:
        out["start"] = iso_hits[0]
        if len(iso_hits) > 1:
            out["end"] = iso_hits[-1]
        elif _NOW_END_TOKENS.search(prose):
            out["end"] = date.today().isoformat()
        return out
    vn_hits = list(_VN_DATE_IN_TEXT.finditer(prose))
    if vn_hits:
        first = _parse_vn_date_token(
            vn_hits[0].group(1), vn_hits[0].group(2), vn_hits[0].group(3)
        )
        if first:
            out["start"] = first
        if len(vn_hits) > 1:
            last = _parse_vn_date_token(
                vn_hits[-1].group(1), vn_hits[-1].group(2), vn_hits[-1].group(3)
            )
            if last:
                out["end"] = last
        elif _NOW_END_TOKENS.search(prose):
            out["end"] = date.today().isoformat()
    return out


def effective_time_range_from_brief(brief: dict[str, Any] | Any) -> dict[str, Any]:
    """Merge time_range from brief fields, requirements, filters, and clarify prose."""
    if hasattr(brief, "model_dump"):
        data = brief.model_dump(mode="json")
    elif isinstance(brief, dict):
        data = brief
    else:
        data = {}

    candidates: list[dict[str, Any]] = []
    tr = data.get("time_range")
    if isinstance(tr, dict):
        candidates.append(tr)

    for req in data.get("requirements") or []:
        if not isinstance(req, dict):
            continue
        if str(req.get("kind") or "").lower() != "time":
            continue
        val = req.get("value")
        if isinstance(val, dict):
            candidates.append(val)
        elif val:
            parsed = _extract_time_range_from_text(str(val))
            if parsed:
                candidates.append(parsed)
        evidence = str(req.get("evidence_quote") or "")
        parsed_ev = _extract_time_range_from_text(evidence)
        if parsed_ev:
            candidates.append(parsed_ev)

    filters = data.get("filters") if isinstance(data.get("filters"), dict) else {}
    for key in ("start", "end", "date_from", "date_to", "time_start", "time_end"):
        raw = filters.get(key)
        if raw and not looks_like_prose_placeholder(raw):
            slot = "start" if key in {"start", "date_from", "time_start"} else "end"
            candidates.append({slot: str(raw)})

    for blob_key in ("clarify_note", "time_note", "date_note"):
        note = filters.get(blob_key)
        if note:
            parsed = _extract_time_range_from_text(str(note))
            if parsed:
                candidates.append(parsed)

    intent = str(data.get("intent") or "")
    parsed_intent = _extract_time_range_from_text(intent)
    if parsed_intent:
        candidates.append(parsed_intent)

    merged: dict[str, Any] = {}
    for cand in candidates:
        coerced = coerce_time_range(cand)
        if coerced.get("start") and not merged.get("start"):
            merged["start"] = coerced["start"]
        if coerced.get("end") and not merged.get("end"):
            merged["end"] = coerced["end"]
        if coerced.get("grain") and not merged.get("grain"):
            merged["grain"] = coerced["grain"]

    if merged.get("start") or merged.get("end"):
        return _shift_off_by_one_year_as_today(merged)
    return merged


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
                return _shift_off_by_one_year_as_today(out)
    if isinstance(value, str) and value.strip() and not looks_like_prose_placeholder(value):
        parsed = _extract_time_range_from_text(value)
        if parsed.get("start") or parsed.get("end"):
            return _shift_off_by_one_year_as_today(parsed)
    fb = fallback if isinstance(fallback, dict) else {}
    out: dict[str, Any] = {}
    if fb.get("start"):
        out["start"] = str(fb["start"])
    if fb.get("end"):
        out["end"] = str(fb["end"])
    if fb.get("grain"):
        out["grain"] = fb["grain"]
    return _shift_off_by_one_year_as_today(out) if out else out


def _shift_off_by_one_year_as_today(tr: dict[str, Any]) -> dict[str, Any]:
    """Fix Agent-I slips that treat last calendar year as 'today'.

    When end's month/day matches today (or ±1 day) but year is today-1, shift
    start/end into the current year. Does not rewrite older historical windows.
    """
    end_raw = str(tr.get("end") or "").strip()[:10]
    start_raw = str(tr.get("start") or "").strip()[:10]
    if not _ISO_DATE.match(end_raw):
        return tr
    try:
        end = datetime.strptime(end_raw, "%Y-%m-%d").date()
    except ValueError:
        return tr
    today = date.today()
    if end.year != today.year - 1:
        return tr
    try:
        end_as_this_year = date(today.year, end.month, end.day)
    except ValueError:
        return tr
    if abs((end_as_this_year - today).days) > 1:
        return tr
    out = dict(tr)
    out["end"] = min(end_as_this_year, today).isoformat()
    if _ISO_DATE.match(start_raw):
        try:
            start = datetime.strptime(start_raw, "%Y-%m-%d").date()
            if start.year == end.year:
                start_as = date(today.year, start.month, start.day)
                if start_as > today:
                    start_as = date(today.year - 1, start.month, start.day)
                out["start"] = start_as.isoformat()
        except ValueError:
            pass
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
