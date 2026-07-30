"""Flexible Parameter Pattern T-SQL builders (LLM never authors SQL)."""

from __future__ import annotations

from typing import Any

from project_core.domain.data_fetch.builders import (
    _codes,
    _limit,
    _require_date,
    _require_ident,
    _sql_str,
)

ALLOWED_FILTER_OPS = frozenset(
    {
        "eq",
        "ne",
        "in",
        "not_in",
        "gte",
        "lte",
        "gt",
        "lt",
        "between",
        "contains",
        "startswith",
        "is_null",
        "is_not_null",
    }
)
ALLOWED_AGG_FNS = frozenset({"sum", "count", "count_distinct", "min", "max", "avg"})


def _sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return _sql_str(str(value))


def _compile_filter(clause: dict[str, Any]) -> str:
    if not isinstance(clause, dict):
        raise ValueError("invalid_filter_clause")
    col = _require_ident(clause.get("column") or clause.get("col") or "")
    op = str(clause.get("op") or clause.get("operator") or "eq").strip().lower()
    if op not in ALLOWED_FILTER_OPS:
        raise ValueError(f"filter_op_not_allowed:{op}")
    value = clause.get("value")
    if op == "is_null":
        return f"{col} IS NULL"
    if op == "is_not_null":
        return f"{col} IS NOT NULL"
    if op in {"in", "not_in"}:
        raw = value if isinstance(value, list) else [value]
        ids = _codes(raw) if all(isinstance(x, str) or x is None for x in raw) else [
            str(x).strip() for x in raw if str(x).strip()
        ]
        if not ids:
            raise ValueError(f"empty_in_list:{col}")
        joined = ", ".join(_sql_literal(x) for x in ids)
        return f"{col} {'NOT IN' if op == 'not_in' else 'IN'} ({joined})"
    if op == "between":
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError("between_needs_two_values")
        return f"{col} BETWEEN {_sql_literal(value[0])} AND {_sql_literal(value[1])}"
    if op == "contains":
        return f"LOWER({col}) LIKE '%' + LOWER({_sql_str(str(value))}) + '%'"
    if op == "startswith":
        return f"LOWER({col}) LIKE LOWER({_sql_str(str(value))}) + '%'"
    sql_op = {
        "eq": "=",
        "ne": "<>",
        "gte": ">=",
        "lte": "<=",
        "gt": ">",
        "lt": "<",
    }[op]
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"{col} {sql_op} {value}"
    if op == "eq":
        return f"LOWER(RTRIM(CAST({col} AS NVARCHAR(4000)))) = LOWER({_sql_str(str(value))})"
    return f"{col} {sql_op} {_sql_literal(value)}"


def normalize_sugar_to_filters(args: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """Compile optional aliases into filters[]; does not mutate unknown keys away."""
    filters = [dict(c) for c in (args.get("filters") or []) if isinstance(c, dict)]
    repairs: list[str] = []

    def _add(column: str, op: str, value: Any, alias: str) -> None:
        nonlocal filters
        filters.append({"column": column, "op": op, "value": value})
        repairs.append(f"{alias}->filter:{column}:{op}")

    if args.get("sku_ids") is not None:
        _add("SKU_ID", "in", args["sku_ids"], "sku_ids")
    if args.get("trans_nums") is not None:
        _add("TRANS_NUM", "in", args["trans_nums"], "trans_nums")
    if args.get("card_ids") is not None:
        _add("CARD_ID", "in", args["card_ids"], "card_ids")
    if args.get("min_amount") is not None and str(args.get("min_amount")).strip() != "":
        _add("AMOUNT", "gte", args["min_amount"], "min_amount")
    if args.get("store_ids") is not None:
        _add("STK_ID", "in", args["store_ids"], "store_ids")
    for key, value in (args.get("equals") or {}).items():
        _add(str(key), "eq", value, f"equals.{key}")
    for key, value in (args.get("contains") or {}).items():
        if isinstance(args.get("contains"), dict):
            _add(str(key), "contains", value, f"contains.{key}")
    if args.get("contains") is not None and not isinstance(args.get("contains"), dict):
        # lookup_distinct style single contains for a column already set
        pass
    return filters, repairs


def build_query_rows(
    *,
    table: str,
    columns: list[str] | None = None,
    time_range: dict[str, Any] | None = None,
    filters: list[dict[str, Any]] | None = None,
    order_by: list[dict[str, Any] | str] | None = None,
    limit: Any = 5000,
    hard_max: int = 50000,
    require_time: bool = False,
    physical_table: str | None = None,
) -> str:
    tbl = _require_ident(physical_table or table)
    top = _limit(limit, default=5000, hard_max=hard_max)
    if columns:
        cols = ", ".join(_require_ident(c) for c in columns[:80])
    else:
        cols = "*"
    predicates: list[str] = []
    tr = time_range or {}
    # Only fact tables (require_time=True) get TRAN_DATE pushdown.
    # Passing brief time_range onto masters (CUSTOMER/CSCARD) must not invent TRAN_DATE.
    if require_time:
        if not tr.get("start"):
            raise ValueError("pushdown_required:time_range")
        start = _require_date("start", tr.get("start"))
        end = _require_date("end", tr.get("end") or start)
        predicates.append(f"TRAN_DATE >= {_sql_str(start)}")
        predicates.append(f"TRAN_DATE <= {_sql_str(end)}")
    for clause in filters or []:
        predicates.append(_compile_filter(clause))
    where = (" WHERE " + " AND ".join(predicates)) if predicates else ""
    order_parts: list[str] = []
    for item in order_by or []:
        if isinstance(item, str):
            order_parts.append(_require_ident(item))
            continue
        if not isinstance(item, dict):
            continue
        col = _require_ident(item.get("column") or item.get("by") or "")
        direction = str(item.get("dir") or item.get("direction") or "asc").upper()
        if direction not in {"ASC", "DESC"}:
            direction = "ASC"
        order_parts.append(f"{col} {direction}")
    order_clause = f" ORDER BY {', '.join(order_parts)}" if order_parts else ""
    return f"SELECT TOP {top} {cols} FROM {tbl}{where}{order_clause}"


def build_aggregate_rows(
    *,
    table: str,
    time_range: dict[str, Any] | None = None,
    filters: list[dict[str, Any]] | None = None,
    group_by: list[str] | None = None,
    aggs: list[dict[str, Any]] | None = None,
    limit: Any = 5000,
    hard_max: int = 50000,
    require_time: bool = False,
    physical_table: str | None = None,
) -> str:
    tbl = _require_ident(physical_table or table)
    top = _limit(limit, default=5000, hard_max=hard_max)
    if not aggs:
        raise ValueError("aggs_required")
    metric_exprs: list[str] = []
    for raw in aggs:
        if not isinstance(raw, dict):
            raise ValueError("invalid_agg")
        fn = str(raw.get("fn") or raw.get("op") or raw.get("agg") or "").strip().lower()
        if fn not in ALLOWED_AGG_FNS:
            raise ValueError(f"agg_fn_not_allowed:{fn}")
        alias = str(raw.get("as") or raw.get("alias") or f"{fn}_{(raw.get('column') or 'x')}").strip()
        alias = _require_ident(alias.replace(".", "_"))
        if fn == "count" and not raw.get("column"):
            metric_exprs.append(f"COUNT(*) AS {alias}")
            continue
        col = _require_ident(raw.get("column") or "")
        if fn == "count":
            metric_exprs.append(f"COUNT({col}) AS {alias}")
        elif fn == "count_distinct":
            metric_exprs.append(f"COUNT(DISTINCT {col}) AS {alias}")
        elif fn == "sum":
            metric_exprs.append(f"SUM({col}) AS {alias}")
        elif fn == "min":
            metric_exprs.append(f"MIN({col}) AS {alias}")
        elif fn == "max":
            metric_exprs.append(f"MAX({col}) AS {alias}")
        elif fn == "avg":
            metric_exprs.append(f"AVG({col}) AS {alias}")
    groups = [_require_ident(g) for g in (group_by or [])]
    predicates: list[str] = []
    tr = time_range or {}
    if require_time:
        if not tr.get("start"):
            raise ValueError("pushdown_required:time_range")
        start = _require_date("start", tr.get("start"))
        end = _require_date("end", tr.get("end") or start)
        predicates.append(f"TRAN_DATE >= {_sql_str(start)}")
        predicates.append(f"TRAN_DATE <= {_sql_str(end)}")
    for clause in filters or []:
        predicates.append(_compile_filter(clause))
    where = (" WHERE " + " AND ".join(predicates)) if predicates else ""
    select_cols = (", ".join(groups) + ", " if groups else "") + ", ".join(metric_exprs)
    group_clause = f" GROUP BY {', '.join(groups)}" if groups else ""
    return f"SELECT TOP {top} {select_cols} FROM {tbl}{where}{group_clause}"


def build_lookup_distinct(
    *,
    table: str,
    column: str,
    time_range: dict[str, Any] | None = None,
    contains: Any = None,
    filters: list[dict[str, Any]] | None = None,
    limit: Any = 30,
    hard_max: int = 100,
    require_time: bool = False,
    physical_table: str | None = None,
) -> str:
    tbl = _require_ident(physical_table or table)
    col = _require_ident(column)
    top = _limit(limit, default=30, hard_max=min(100, hard_max))
    predicates: list[str] = []
    tr = time_range or {}
    if require_time:
        if not tr.get("start"):
            raise ValueError("pushdown_required:time_range")
        start = _require_date("start", tr.get("start"))
        end = _require_date("end", tr.get("end") or start)
        predicates.append(f"TRAN_DATE >= {_sql_str(start)} AND TRAN_DATE <= {_sql_str(end)}")
    if contains is not None and str(contains).strip():
        predicates.append(
            f"LOWER({col}) LIKE '%' + LOWER({_sql_str(str(contains).strip())}) + '%'"
        )
    for clause in filters or []:
        predicates.append(_compile_filter(clause))
    where = (" WHERE " + " AND ".join(predicates)) if predicates else ""
    return (
        f"SELECT TOP {top} {col} AS code_value, COUNT(*) AS cnt "
        f"FROM {tbl}{where} GROUP BY {col} ORDER BY COUNT(*) DESC"
    )
