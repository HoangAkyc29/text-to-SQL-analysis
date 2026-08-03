"""Shared text-search options: case-insensitive + substring LIKE (default ON)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchOpts:
    """Defaults ON — caller must pass False to disable for one search instance."""

    case_insensitive: bool = True
    fuzzy: bool = True  # LIKE %substring%; False → exact equality


DEFAULT_SEARCH = SearchOpts()


def _norm_expr(column_sql: str, *, case_insensitive: bool) -> str:
    """column_sql may be a bare name or expression (e.g. LTRIM(RTRIM(CARD_ID)))."""
    base = f"LTRIM(RTRIM(CAST({column_sql} AS NVARCHAR(4000))))"
    if case_insensitive:
        return f"LOWER({base})"
    return base


def bind_value(raw: str, opts: SearchOpts) -> str:
    v = (raw or "").strip()
    if opts.case_insensitive:
        v = v.lower()
    if opts.fuzzy:
        return f"%{v}%"
    return v


def bind_prefix(raw: str, opts: SearchOpts) -> str:
    """Starts-with pattern for 'tiền tố' fields.

    fuzzy ON  → ``prefix%`` (not ``%prefix%``)
    fuzzy OFF → exact equality value (no wildcards)
    """
    v = (raw or "").strip()
    if opts.case_insensitive:
        v = v.lower()
    if opts.fuzzy:
        return f"{v}%"
    return v


def match_column(column_sql: str, opts: SearchOpts) -> str:
    """SQL fragment with one `?` placeholder for bind_value(...)."""
    left = _norm_expr(column_sql, case_insensitive=opts.case_insensitive)
    op = "LIKE" if opts.fuzzy else "="
    return f"{left} {op} ?"


def match_prefix_column(column_sql: str, opts: SearchOpts) -> str:
    """Prefix / exact match — use with bind_prefix(...)."""
    left = _norm_expr(column_sql, case_insensitive=opts.case_insensitive)
    op = "LIKE" if opts.fuzzy else "="
    return f"{left} {op} ?"


def match_prefix_column_fact(column_sql: str, opts: SearchOpts) -> str:
    """Fact-table prefix: avoid LOWER(CAST(...)) so indexes can still help.

    Relies on SQL Server CI collation for case; still trims CHAR padding.
    Use with ``bind_prefix`` (same as match_prefix_column).
    """
    left = f"LTRIM(RTRIM({column_sql}))"
    op = "LIKE" if opts.fuzzy else "="
    return f"{left} {op} ?"


def match_any(columns: list[str], opts: SearchOpts) -> str:
    """OR of match_column for each column — same bind value repeated len(columns) times."""
    parts = [match_column(c, opts) for c in columns]
    if len(parts) == 1:
        return parts[0]
    return "(" + " OR ".join(parts) + ")"


def expand_params(value: str, column_count: int, opts: SearchOpts) -> list[str]:
    bound = bind_value(value, opts)
    return [bound] * column_count


def expand_prefix_params(value: str, column_count: int, opts: SearchOpts) -> list[str]:
    bound = bind_prefix(value, opts)
    return [bound] * column_count


def resolve_search_limit(override: int | None = None) -> int:
    """Effective TOP for master searches (SKU / CSCARD)."""
    from app.config import settings

    if override is not None:
        return max(1, int(override))
    return max(1, int(settings.search_limit))


def mark_truncated(df, limit: int):
    """Attach truncation metadata used by UI status / resolve guards."""
    df.attrs["truncated"] = len(df) >= int(limit)
    df.attrs["limit"] = int(limit)
    return df


def raise_if_truncated(df, *, what: str) -> None:
    if not getattr(df, "attrs", {}).get("truncated"):
        return
    lim = df.attrs.get("limit")
    raise ValueError(
        f"{what} khớp ≥{lim} dòng (đã cắt TOP). "
        "Thu hẹp điều kiện hoặc tắt «Tìm gần đúng»."
    )