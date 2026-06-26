"""Safe condition evaluator for graph routing (no eval())."""

from __future__ import annotations

import re
from typing import Any

_BOOL = {"true": True, "false": False, "null": None, "none": None}

_SIMPLE_RE = re.compile(
    r"^([a-zA-Z_][\w.]*)\s*(==|!=)\s*(.+)$"
)
_IN_RE = re.compile(
    r"^([a-zA-Z_][\w.]*)\s+in\s+\[(.+)\]$"
)


def _resolve_path(ctx: dict[str, Any], path: str) -> Any:
    """Resolve dot-path like ``inbox.agent-alpha.risk`` against *ctx*."""
    parts = path.split(".")
    cur: Any = ctx
    for part in parts:
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def _parse_literal(raw: str) -> Any:
    text = raw.strip()
    if (text.startswith("'") and text.endswith("'")) or (
        text.startswith('"') and text.endswith('"')
    ):
        return text[1:-1]
    lower = text.lower()
    if lower in _BOOL:
        return _BOOL[lower]
    if text.isdigit() or (text.startswith("-") and text[1:].isdigit()):
        return int(text)
    try:
        return float(text)
    except ValueError:
        return text


def _eval_atom(expr: str, ctx: dict[str, Any]) -> bool:
    expr = expr.strip()
    if not expr:
        return True

    m = _IN_RE.match(expr)
    if m:
        left = _resolve_path(ctx, m.group(1))
        items = [_parse_literal(x.strip()) for x in m.group(2).split(",") if x.strip()]
        return left in items

    m = _SIMPLE_RE.match(expr)
    if m:
        left = _resolve_path(ctx, m.group(1))
        op = m.group(2)
        right = _parse_literal(m.group(3))
        if op == "==":
            return left == right
        return left != right

    # Bare path: truthy check
    val = _resolve_path(ctx, expr)
    return bool(val)


def evaluate_condition(expr: str | None, ctx: dict[str, Any]) -> bool:
    """Evaluate a condition string against *ctx*.

    Supports ``==``, ``!=``, ``in [...]``, ``and``, ``or``.
    """
    if expr is None or expr.strip().lower() == "else":
        return True
    text = expr.strip()

    if " or " in text:
        return any(evaluate_condition(part, ctx) for part in text.split(" or "))

    if " and " in text:
        return all(evaluate_condition(part, ctx) for part in text.split(" and "))

    return _eval_atom(text, ctx)


class ConditionEvaluator:
    """Evaluate routing conditions against an execution context."""

    def __init__(self, ctx: dict[str, Any]) -> None:
        self._ctx = ctx

    def matches(self, expr: str | None) -> bool:
        return evaluate_condition(expr, self._ctx)

    def pick_route(self, routes: list[tuple[str | None, str]]) -> str | None:
        """Return the first matching route target, or None."""
        for when, target in routes:
            if when is None or when.strip().lower() == "else":
                return target
            if self.matches(when):
                return target
        return None
