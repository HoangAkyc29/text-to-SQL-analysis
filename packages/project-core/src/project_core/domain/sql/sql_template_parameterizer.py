from __future__ import annotations

import re
from typing import Any

_PLACEHOLDER_PATTERNS = [
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), ":date"),
    (re.compile(r"\b\d{5,}\b"), ":number"),
    (re.compile(r"'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'"), ":email"),
    (re.compile(r"'0\d{8,10}'"), ":phone"),
]


def parameterize_sql(sql: str) -> str:
    out = sql
    for pattern, replacement in _PLACEHOLDER_PATTERNS:
        out = pattern.sub(replacement, out)
    return out


def parameterize_brief_values(values: dict[str, Any]) -> dict[str, Any]:
    def _walk(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _walk(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_walk(v) for v in obj]
        if isinstance(obj, str):
            for pattern, replacement in _PLACEHOLDER_PATTERNS:
                if pattern.search(obj):
                    return replacement
        return obj

    return _walk(values)
