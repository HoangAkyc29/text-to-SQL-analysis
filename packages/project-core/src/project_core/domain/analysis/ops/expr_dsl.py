"""Safe expression DSL for add_column_expr (AST allowlist, no free Python)."""

from __future__ import annotations

import ast
from typing import Any

import pandas as pd

_ALLOWED_FUNCS = {
    "coalesce",
    "length",
    "lower",
    "upper",
    "trim",
    "substr",
    "year",
    "month",
    "day",
    "abs",
    "round",
}


class _ExprError(ValueError):
    pass


def eval_column_expr(df: pd.DataFrame, expr: str) -> pd.Series:
    """Evaluate a narrow expression against dataframe columns.

    Supported:
    - column names as bare identifiers
    - numeric/string literals
    - +, -, *, /, //, %
    - coalesce(a, b, ...), length(c), lower/upper/trim(c), substr(c, start, len)
    - year/month/day(c), abs(c), round(c, n)
    """
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except SyntaxError as exc:
        raise _ExprError(f"invalid_expr:{exc}") from exc
    return _eval_node(tree.body, df)


def _eval_node(node: ast.AST, df: pd.DataFrame) -> Any:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, df)
    if isinstance(node, ast.Name):
        if node.id not in df.columns:
            raise _ExprError(f"unknown_column:{node.id}")
        return df[node.id]
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        val = _eval_node(node.operand, df)
        return val if isinstance(node.op, ast.UAdd) else -val
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left, df)
        right = _eval_node(node.right, df)
        op = node.op
        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            return left / right
        if isinstance(op, ast.FloorDiv):
            return left // right
        if isinstance(op, ast.Mod):
            return left % right
        raise _ExprError(f"unsupported_binop:{type(op).__name__}")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise _ExprError("only_simple_calls_allowed")
        fname = node.func.id
        if fname not in _ALLOWED_FUNCS:
            raise _ExprError(f"forbidden_func:{fname}")
        args = [_eval_node(a, df) for a in node.args]
        return _call_func(fname, args)
    raise _ExprError(f"unsupported_node:{type(node).__name__}")


def _call_func(name: str, args: list[Any]) -> Any:
    if name == "coalesce":
        if not args:
            raise _ExprError("coalesce_needs_args")
        out = args[0]
        for a in args[1:]:
            out = out.fillna(a) if isinstance(out, pd.Series) else (a if out is None else out)
        return out
    if name == "length":
        s = args[0]
        return s.astype(str).str.len()
    if name == "lower":
        return args[0].astype(str).str.lower()
    if name == "upper":
        return args[0].astype(str).str.upper()
    if name == "trim":
        return args[0].astype(str).str.strip()
    if name == "substr":
        s, start, length = args[0], int(args[1]), int(args[2])
        return s.astype(str).str.slice(start, start + length)
    if name in {"year", "month", "day"}:
        dt = pd.to_datetime(args[0], errors="coerce")
        return getattr(dt.dt, name)
    if name == "abs":
        return abs(args[0]) if not isinstance(args[0], pd.Series) else args[0].abs()
    if name == "round":
        ndigits = int(args[1]) if len(args) > 1 else 0
        return args[0].round(ndigits) if isinstance(args[0], pd.Series) else round(args[0], ndigits)
    raise _ExprError(f"forbidden_func:{name}")
