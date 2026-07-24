"""Safe parameterized T-SQL builders for DataFetchToolkit.

LLM never sees or edits these strings. Values are validated then inlined as
literals suitable for PolicyEngine + sql-gateway (no pyodbc params required).
"""

from __future__ import annotations

import re
from typing import Any

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_CODE_RE = re.compile(r"^[A-Za-z0-9._\-/]+$")


def _sql_str(value: str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def _require_date(label: str, value: Any) -> str:
    text = str(value or "").strip()[:10]
    if not _DATE_RE.match(text):
        raise ValueError(f"invalid_date:{label}")
    return text


def _require_ident(name: str) -> str:
    text = str(name or "").strip()
    if not _IDENT_RE.match(text):
        raise ValueError(f"invalid_identifier:{name}")
    return text.upper() if text.upper() == text or text.isupper() else text


def _codes(values: Any) -> list[str]:
    if values is None:
        return []
    raw = values if isinstance(values, list) else [values]
    out: list[str] = []
    for item in raw:
        text = str(item).strip()
        if not text:
            continue
        if not _CODE_RE.match(text) or len(text) > 64:
            raise ValueError(f"invalid_code:{text[:40]}")
        out.append(text)
    return out


def _limit(value: Any, *, default: int, hard_max: int) -> int:
    try:
        n = int(value if value is not None else default)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid_limit") from exc
    return max(1, min(n, hard_max))


def _sku_code_match_clause(codes: list[str]) -> str:
    """Exact SKU_CODE match, or leading-zero-normalized equality.

    Avoids substring LIKE '%30325%' which matches unrelated padded codes
    such as 02130325 / 04130325.
    """
    parts: list[str] = []
    for code in codes:
        lit = _sql_str(code)
        stripped = code.lstrip("0") or "0"
        strip_lit = _sql_str(stripped)
        # PATINDEX + SUBSTRING strips leading zeros on the DB side.
        parts.append(
            "("
            f"LOWER(RTRIM(SKU_CODE)) = LOWER({lit}) OR "
            "LOWER(SUBSTRING(RTRIM(SKU_CODE), "
            "PATINDEX('%[^0]%', RTRIM(SKU_CODE) + 'x'), 64)) = "
            f"LOWER({strip_lit})"
            ")"
        )
    return "(" + " OR ".join(parts) + ")"


def build_resolve_products(*, codes: Any, limit: Any = 50, hard_max: int = 500) -> str:
    code_list = _codes(codes)
    if not code_list:
        raise ValueError("codes_required")
    top = _limit(limit, default=50, hard_max=min(500, hard_max))
    where = _sku_code_match_clause(code_list)
    return (
        f"SELECT TOP {top} SKU_ID, SKU_CODE, FULL_NAME "
        f"FROM SKU_DEF WHERE {where} ORDER BY SKU_CODE"
    )


def build_preview_table(
    *,
    table: str,
    columns: list[str] | None = None,
    time_range: dict[str, Any] | None = None,
    equals: dict[str, Any] | None = None,
    contains: dict[str, Any] | None = None,
    limit: Any = 20,
    hard_max: int = 50,
    require_time: bool = False,
) -> str:
    tbl = _require_ident(table)
    top = _limit(limit, default=20, hard_max=min(50, hard_max))
    if columns:
        cols = ", ".join(_require_ident(c) for c in columns[:30])
    else:
        cols = "*"
    predicates: list[str] = []
    tr = time_range or {}
    if require_time or tr.get("start") or tr.get("end"):
        start = _require_date("start", tr.get("start"))
        end = _require_date("end", tr.get("end") or tr.get("start"))
        predicates.append(f"TRAN_DATE >= {_sql_str(start)} AND TRAN_DATE <= {_sql_str(end)}")
    elif require_time:
        raise ValueError("pushdown_required:time_range")
    for key, value in (equals or {}).items():
        col = _require_ident(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            predicates.append(f"{col} = {value}")
        else:
            predicates.append(f"LOWER({col}) = LOWER({_sql_str(str(value))})")
    for key, value in (contains or {}).items():
        col = _require_ident(key)
        predicates.append(
            f"LOWER({col}) LIKE '%' + LOWER({_sql_str(str(value))}) + '%'"
        )
    where = (" WHERE " + " AND ".join(predicates)) if predicates else ""
    return f"SELECT TOP {top} {cols} FROM {tbl}{where}"


def build_fetch_sale_lines(
    *,
    sku_ids: Any,
    time_range: dict[str, Any],
    store_ids: list[int] | None = None,
    limit: Any = 5000,
    hard_max: int = 50000,
    physical_table: str = "STRANS",
) -> str:
    ids = _codes(sku_ids)
    if not ids:
        raise ValueError("sku_ids_required")
    start = _require_date("start", (time_range or {}).get("start"))
    end = _require_date("end", (time_range or {}).get("end") or start)
    top = _limit(limit, default=5000, hard_max=hard_max)
    tbl = _require_ident(physical_table)
    id_list = ", ".join(_sql_str(i) for i in ids)
    predicates = [
        f"TRAN_DATE >= {_sql_str(start)}",
        f"TRAN_DATE <= {_sql_str(end)}",
        f"SKU_ID IN ({id_list})",
    ]
    if store_ids:
        stores = ", ".join(str(int(s)) for s in store_ids)
        predicates.append(f"STK_ID IN ({stores})")
    where = " AND ".join(predicates)
    return (
        f"SELECT TOP {top} TRANS_NUM, TRAN_DATE, TRAN_TIME, STK_ID, SKU_ID, "
        f"TRANS_CODE, QTY, AMOUNT "
        f"FROM {tbl} WHERE {where} "
        f"ORDER BY TRAN_DATE DESC, TRAN_TIME DESC"
    )


def build_fetch_bill_headers(
    *,
    time_range: dict[str, Any],
    trans_nums: Any = None,
    min_amount: Any = None,
    store_ids: list[int] | None = None,
    limit: Any = 5000,
    hard_max: int = 50000,
    physical_table: str = "TRANSHDR",
) -> str:
    start = _require_date("start", (time_range or {}).get("start"))
    end = _require_date("end", (time_range or {}).get("end") or start)
    top = _limit(limit, default=5000, hard_max=hard_max)
    tbl = _require_ident(physical_table)
    predicates = [
        f"TRAN_DATE >= {_sql_str(start)}",
        f"TRAN_DATE <= {_sql_str(end)}",
    ]
    nums = _codes(trans_nums)
    if nums:
        predicates.append("TRANS_NUM IN (" + ", ".join(_sql_str(n) for n in nums) + ")")
    if min_amount is not None and str(min_amount).strip() != "":
        try:
            amount = float(min_amount)
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid_min_amount") from exc
        predicates.append(f"AMOUNT >= {amount}")
    if store_ids:
        stores = ", ".join(str(int(s)) for s in store_ids)
        predicates.append(f"STK_ID IN ({stores})")
    where = " AND ".join(predicates)
    return (
        f"SELECT TOP {top} TRANS_NUM, TRAN_DATE, TRAN_TIME, STK_ID, TRANS_CODE, AMOUNT "
        f"FROM {tbl} WHERE {where} "
        f"ORDER BY TRAN_DATE DESC, TRAN_TIME DESC"
    )


def build_fetch_lines_for_bills(
    *,
    trans_nums: Any,
    time_range: dict[str, Any],
    sku_ids: Any = None,
    limit: Any = 20000,
    hard_max: int = 50000,
    physical_table: str = "STRANS",
) -> str:
    nums = _codes(trans_nums)
    if not nums:
        raise ValueError("trans_nums_required")
    start = _require_date("start", (time_range or {}).get("start"))
    end = _require_date("end", (time_range or {}).get("end") or start)
    top = _limit(limit, default=20000, hard_max=hard_max)
    tbl = _require_ident(physical_table)
    predicates = [
        f"TRAN_DATE >= {_sql_str(start)}",
        f"TRAN_DATE <= {_sql_str(end)}",
        "TRANS_NUM IN (" + ", ".join(_sql_str(n) for n in nums) + ")",
    ]
    ids = _codes(sku_ids)
    if ids:
        predicates.append("SKU_ID IN (" + ", ".join(_sql_str(i) for i in ids) + ")")
    where = " AND ".join(predicates)
    return (
        f"SELECT TOP {top} TRANS_NUM, TRAN_DATE, TRAN_TIME, STK_ID, SKU_ID, "
        f"TRANS_CODE, QTY, AMOUNT "
        f"FROM {tbl} WHERE {where} "
        f"ORDER BY TRANS_NUM, TRAN_DATE, TRAN_TIME"
    )


def build_aggregate_metric(
    *,
    time_range: dict[str, Any],
    metrics: list[str],
    group_by: list[str] | None = None,
    sku_ids: Any = None,
    store_ids: list[int] | None = None,
    limit: Any = 5000,
    hard_max: int = 50000,
    physical_table: str = "STRANS",
) -> str:
    from project_core.domain.data_fetch.catalog import ALLOWED_AGG_GROUP_BY, ALLOWED_AGG_METRICS

    start = _require_date("start", (time_range or {}).get("start"))
    end = _require_date("end", (time_range or {}).get("end") or start)
    top = _limit(limit, default=5000, hard_max=hard_max)
    tbl = _require_ident(physical_table)
    metric_exprs: list[str] = []
    for m in metrics or []:
        key = str(m).strip().lower()
        if key not in ALLOWED_AGG_METRICS:
            raise ValueError(f"metric_not_allowed:{m}")
        if key == "sum_qty":
            metric_exprs.append("SUM(QTY) AS sum_qty")
        elif key == "sum_amount":
            metric_exprs.append("SUM(AMOUNT) AS sum_amount")
        elif key == "count_rows":
            metric_exprs.append("COUNT(*) AS count_rows")
        elif key == "count_bills":
            metric_exprs.append("COUNT(DISTINCT TRANS_NUM) AS count_bills")
    if not metric_exprs:
        raise ValueError("metrics_required")
    groups: list[str] = []
    for g in group_by or []:
        col = _require_ident(g)
        if col.upper() not in ALLOWED_AGG_GROUP_BY:
            raise ValueError(f"group_by_not_allowed:{g}")
        groups.append(col.upper())
    predicates = [
        f"TRAN_DATE >= {_sql_str(start)}",
        f"TRAN_DATE <= {_sql_str(end)}",
    ]
    ids = _codes(sku_ids)
    if ids:
        predicates.append("SKU_ID IN (" + ", ".join(_sql_str(i) for i in ids) + ")")
    if store_ids:
        predicates.append("STK_ID IN (" + ", ".join(str(int(s)) for s in store_ids) + ")")
    where = " AND ".join(predicates)
    select_cols = (", ".join(groups) + ", " if groups else "") + ", ".join(metric_exprs)
    group_clause = f" GROUP BY {', '.join(groups)}" if groups else ""
    return f"SELECT TOP {top} {select_cols} FROM {tbl} WHERE {where}{group_clause}"


def build_lookup_codes(
    *,
    table: str,
    column: str,
    time_range: dict[str, Any] | None = None,
    contains: Any = None,
    limit: Any = 30,
    hard_max: int = 100,
    require_time: bool = False,
) -> str:
    tbl = _require_ident(table)
    col = _require_ident(column)
    top = _limit(limit, default=30, hard_max=min(100, hard_max))
    predicates: list[str] = []
    tr = time_range or {}
    if require_time or tr.get("start") or tr.get("end"):
        start = _require_date("start", tr.get("start"))
        end = _require_date("end", tr.get("end") or start)
        predicates.append(f"TRAN_DATE >= {_sql_str(start)} AND TRAN_DATE <= {_sql_str(end)}")
    elif require_time:
        raise ValueError("pushdown_required:time_range")
    if contains is not None and str(contains).strip():
        predicates.append(
            f"LOWER({col}) LIKE '%' + LOWER({_sql_str(str(contains).strip())}) + '%'"
        )
    where = (" WHERE " + " AND ".join(predicates)) if predicates else ""
    return (
        f"SELECT TOP {top} {col} AS code_value, COUNT(*) AS cnt "
        f"FROM {tbl}{where} GROUP BY {col} ORDER BY COUNT(*) DESC"
    )
