"""Filter / sort / slice / shape / inspect / export / agg / join / critic ops."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Callable

import numpy as np
import pandas as pd

from project_core.domain.analysis.ops.expr_dsl import eval_column_expr
from project_core.domain.analysis.ops.working_set import DatasetHandle, DatasetWorkingSet
from project_core.tabular.io import (
    inspect_tabular,
    inspect_workbook,
    neutralize_spreadsheet_formulas,
    read_tabular,
    sha256_file,
)

OpHandler = Callable[[DatasetWorkingSet, dict[str, Any], Path], dict[str, Any]]


def _require_cols(df: pd.DataFrame, cols: list[str]) -> str | None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        return f"missing_columns:{missing}"
    return None


def _as_col_list(value: Any) -> list[str]:
    """Normalize group_by/partition_by/order column specs.

    LLMs often pass a bare string (\"SKU_ID\"); iterating that yields characters.
    Also accept {column: ...} and list[{column, ascending}].
    """
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, dict):
        col = value.get("column") or value.get("col") or value.get("field") or value.get("by")
        if col is None:
            return []
        text = str(col).strip()
        return [text] if text else []
    if isinstance(value, (list, tuple)):
        out: list[str] = []
        for item in value:
            out.extend(_as_col_list(item))
        return out
    text = str(value).strip()
    return [text] if text else []


def _as_order_by(
    value: Any,
    *,
    default_ascending: Any = False,
) -> tuple[list[str], list[bool] | bool]:
    """Normalize order_by to (columns, ascending flags)."""
    if value is None:
        return [], default_ascending
    if isinstance(value, str):
        cols = _as_col_list(value)
        return cols, default_ascending
    if isinstance(value, dict):
        cols = _as_col_list(value)
        if "ascending" in value:
            return cols, bool(value.get("ascending"))
        return cols, default_ascending
    if isinstance(value, (list, tuple)):
        if not value:
            return [], default_ascending
        if all(isinstance(item, dict) for item in value):
            cols: list[str] = []
            ascs: list[bool] = []
            fallback = (
                bool(default_ascending[0])
                if isinstance(default_ascending, list) and default_ascending
                else bool(default_ascending)
            )
            for item in value:
                part = _as_col_list(item)
                if not part:
                    continue
                cols.append(part[0])
                ascs.append(bool(item["ascending"]) if "ascending" in item else fallback)
            return cols, ascs if ascs else default_ascending
        return _as_col_list(value), default_ascending
    return _as_col_list(value), default_ascending


def _save(
    ws: DatasetWorkingSet,
    save_as: str | None,
    df: pd.DataFrame,
    *,
    source: str,
    role: str | None = None,
) -> dict[str, Any]:
    if not save_as:
        return {"row_count": int(len(df)), "columns": [str(c) for c in df.columns]}
    handle = ws.save_frame(
        save_as,
        df,
        role=role,
        source=source,
        op_id=source,
    )
    return {
        "saved_as": handle.ref,
        "row_count": int(len(df)),
        "columns": [str(c) for c in df.columns],
        "path": handle.path,
    }


# ----- A. Inspect -----


def op_list_datasets(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    return {"datasets": ws.list_profiles()}


def op_describe_columns(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    ds = ws.get(str(args["dataset"])).frame()
    cols = args.get("columns") or list(ds.columns)
    err = _require_cols(ds, [str(c) for c in cols])
    if err:
        return {"error": err}
    details = []
    for c in cols:
        s = ds[c]
        entry: dict[str, Any] = {
            "column": str(c),
            "dtype": str(s.dtype),
            "null_frac": float(s.isna().mean()) if len(ds) else 0.0,
            "nunique": int(s.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(s):
            entry["min"] = None if s.dropna().empty else float(s.min())
            entry["max"] = None if s.dropna().empty else float(s.max())
        elif pd.api.types.is_datetime64_any_dtype(s):
            entry["min"] = None if s.dropna().empty else str(s.min())
            entry["max"] = None if s.dropna().empty else str(s.max())
        else:
            top = s.astype(str).value_counts(dropna=True).head(5)
            entry["top_values"] = [{str(k): int(v)} for k, v in top.items()]
        details.append(entry)
    return {"dataset": args["dataset"], "columns": details, "row_count": int(len(ds))}


def op_head_rows(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    ds = ws.get(str(args["dataset"])).frame()
    n = int(args.get("n") or 10)
    rows = ds.head(n).astype(object).where(pd.notnull(ds.head(n)), None)
    return {"dataset": args["dataset"], "rows": rows.to_dict(orient="records"), "n": n}


def op_sample_rows(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    ds = ws.get(str(args["dataset"])).frame()
    n = min(int(args.get("n") or 10), len(ds) if len(ds) else 0)
    seed = args.get("seed")
    sample = ds.sample(n=n, random_state=seed) if n else ds.head(0)
    rows = sample.astype(object).where(pd.notnull(sample), None)
    return {"dataset": args["dataset"], "rows": rows.to_dict(orient="records"), "n": n}


def op_value_counts(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    ds = ws.get(str(args["dataset"])).frame()
    col = str(args["column"])
    err = _require_cols(ds, [col])
    if err:
        return {"error": err}
    top_k = int(args.get("top_k") or 20)
    dropna = bool(args.get("dropna", True))
    vc = ds[col].value_counts(dropna=dropna).head(top_k)
    return {
        "dataset": args["dataset"],
        "column": col,
        "counts": [{str(k): int(v)} for k, v in vc.items()],
    }


def op_null_report(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    ds = ws.get(str(args["dataset"])).frame()
    per_col = {str(c): {"nulls": int(ds[c].isna().sum()), "frac": float(ds[c].isna().mean())} for c in ds.columns}
    row_nulls = int(ds.isna().any(axis=1).sum()) if len(ds) else 0
    return {"dataset": args["dataset"], "per_column": per_col, "rows_with_any_null": row_nulls}


def op_assert_nonempty(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    ds = ws.get(str(args["dataset"])).frame()
    ok = len(ds) > 0
    return {"dataset": args["dataset"], "ok": ok, "row_count": int(len(ds)), "error": None if ok else "empty_dataset"}


def op_assert_columns_present(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    ds = ws.get(str(args["dataset"])).frame()
    cols = [str(c) for c in (args.get("columns") or [])]
    err = _require_cols(ds, cols)
    return {
        "dataset": args["dataset"],
        "ok": err is None,
        "missing": [] if err is None else err.replace("missing_columns:", ""),
        "error": err,
    }


# ----- B. Shape -----


def op_select_columns(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    cols = [str(c) for c in (args.get("columns") or [])]
    err = _require_cols(handle.frame(), cols)
    if err:
        return {"error": err}
    return _save(ws, args.get("save_as"), handle.frame()[cols].copy(), source="select_columns", role=handle.role)


def op_rename_columns(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    mapping = {str(k): str(v) for k, v in (args.get("mapping") or {}).items()}
    err = _require_cols(handle.frame(), list(mapping.keys()))
    if err:
        return {"error": err}
    return _save(ws, args.get("save_as"), handle.frame().rename(columns=mapping), source="rename_columns", role=handle.role)


def op_drop_columns(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    cols = [str(c) for c in (args.get("columns") or [])]
    df = handle.frame().drop(columns=[c for c in cols if c in handle.frame().columns], errors="ignore")
    return _save(ws, args.get("save_as"), df, source="drop_columns", role=handle.role)


def op_cast_column(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    column_value = args.get("column") or args.get("column_name")
    if column_value is None and len(args.get("columns") or []) == 1:
        column_value = args["columns"][0]
    if column_value is None:
        return {"error": "column_required"}
    col = str(column_value)
    to = str(
        args.get("to")
        or args.get("dtype")
        or args.get("target_type")
        or "str"
    ).lower()
    err = _require_cols(handle.frame(), [col])
    if err:
        return {"error": err}
    df = handle.frame().copy()
    if to in {"int", "int64"}:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    elif to in {"float", "float64"}:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    elif to in {"str", "string"}:
        df[col] = df[col].astype(str)
    elif to in {"datetime", "date"}:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    else:
        return {"error": f"unsupported_cast:{to}"}
    return _save(ws, args.get("save_as"), df, source="cast_column", role=handle.role)


def op_add_column_expr(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    name = str(args["name"])
    expr = str(args["expr"])
    try:
        series = eval_column_expr(handle.frame(), expr)
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}
    df = handle.frame().copy()
    df[name] = series
    return _save(ws, args.get("save_as"), df, source="add_column_expr", role=handle.role)


def op_fill_null(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    value = args.get("value")
    cols = args.get("columns")
    df = handle.frame().copy()
    if cols:
        for c in cols:
            if c in df.columns:
                df[c] = df[c].fillna(value)
    else:
        df = df.fillna(value)
    return _save(ws, args.get("save_as"), df, source="fill_null", role=handle.role)


def op_drop_null(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    subset = args.get("columns")
    df = handle.frame().dropna(subset=subset if subset else None)
    return _save(ws, args.get("save_as"), df, source="drop_null", role=handle.role)


# ----- C. Filter -----


def _expand_filter_value(ws: DatasetWorkingSet, value: Any) -> Any:
    """Expand dataset / dataset.column refs in filter values (meta tooling)."""
    from project_core.domain.data_fetch.arg_coerce import looks_like_prose_placeholder

    if isinstance(value, dict):
        ref = (
            value.get("dataset")
            or value.get("ref")
            or value.get("from")
            or value.get("source")
            or value.get("save_as")
        )
        col = value.get("column") or value.get("column_name") or value.get("field")
        if ref is None:
            return value
        ref_s = str(ref).strip()
        if not ws.has(ref_s):
            raise ValueError(f"unknown_dataset_ref:{ref_s}")
        frame = ws.get(ref_s).frame()
        if col is None:
            for preferred in ("SKU_ID", "SKU_CODE", "TRANS_NUM"):
                if preferred in frame.columns:
                    col = preferred
                    break
            if col is None and len(frame.columns):
                col = str(frame.columns[0])
        col_s = str(col)
        if col_s not in frame.columns:
            raise ValueError(f"missing_columns:[{col_s}]")
        return [str(x) for x in frame[col_s].dropna().astype(str).tolist()]

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return value
        # Never treat brief/checklist path placeholders as literal filter values.
        if looks_like_prose_placeholder(text):
            raise ValueError(f"prose_filter_value:{text}")
        # dataset.COLUMN
        if "." in text:
            ref_s, _, col_s = text.partition(".")
            ref_s, col_s = ref_s.strip(), col_s.strip()
            if ref_s and col_s and ws.has(ref_s):
                frame = ws.get(ref_s).frame()
                if col_s in frame.columns:
                    return [str(x) for x in frame[col_s].dropna().astype(str).tolist()]
        # bare dataset ref
        if ws.has(text):
            frame = ws.get(text).frame()
            for preferred in ("SKU_ID", "SKU_CODE", "TRANS_NUM"):
                if preferred in frame.columns:
                    return [str(x) for x in frame[preferred].dropna().astype(str).tolist()]
            if len(frame.columns):
                col0 = str(frame.columns[0])
                return [str(x) for x in frame[col0].dropna().astype(str).tolist()]
        return value

    if isinstance(value, list) and len(value) == 1 and isinstance(value[0], str):
        expanded = _expand_filter_value(ws, value[0])
        if expanded is not value[0]:
            return expanded
    return value


def _normalize_filter_clause(clause: dict[str, Any]) -> dict[str, Any]:
    """Accept planner aliases: operator→op, col/field→column."""
    if not isinstance(clause, dict):
        raise ValueError("invalid_filter_clause")
    out = dict(clause)
    if out.get("column") is None:
        for key in ("column_name", "col", "field"):
            if out.get(key) is not None:
                out["column"] = out[key]
                break
    if out.get("op") is None:
        for key in ("operator", "cmp", "predicate"):
            if out.get(key) is not None:
                out["op"] = out[key]
                break
    if out.get("column") is None:
        raise ValueError("filter_clause_missing_column")
    return out


def _resolve_collided_column(
    df: pd.DataFrame,
    col: str,
    *,
    prefer_left: bool = True,
) -> str | None:
    """Map bare names (AMOUNT) onto join suffixes (AMOUNT_hdr / AMOUNT_x).

    After header⋈line joins, bill totals usually live on the left/header side.
    Prefer ``*_hdr`` / ``*_x`` so min_bill filters keep working without clarify.
    """
    if col in df.columns:
        return col
    upper = {str(c).upper(): str(c) for c in df.columns}
    base = str(col).upper()
    if base in upper:
        return upper[base]
    preferred = [f"{base}_HDR", f"{base}_HEADER", f"{base}_X", f"{base}_LEFT"]
    fallback = [f"{base}_LINE", f"{base}_Y", f"{base}_RIGHT"]
    order = preferred + fallback if prefer_left else fallback + preferred
    for cand in order:
        if cand in upper:
            return upper[cand]
    matches = [c for u, c in upper.items() if u.startswith(base + "_")]
    if not matches:
        return None
    if prefer_left:
        for c in matches:
            if str(c).upper().endswith(("_HDR", "_HEADER", "_X", "_LEFT")):
                return c
    return matches[0]


def _default_join_suffixes(left: pd.DataFrame, right: pd.DataFrame) -> tuple[str, str]:
    overlap = {str(c).upper() for c in left.columns} & {str(c).upper() for c in right.columns}
    if overlap & {"AMOUNT", "TOTAL", "QTY", "TRAN_DATE", "TRAN_TIME", "STK_ID"}:
        return ("_hdr", "_line")
    return ("_x", "_y")


def _clause_mask(df: pd.DataFrame, clause: dict[str, Any]) -> pd.Series:
    clause = _normalize_filter_clause(clause)
    col = str(clause["column"])
    op = str(clause.get("op") or "eq").lower()
    value = clause.get("value")
    case_insensitive = bool(clause.get("case_insensitive", False))
    resolved = _resolve_collided_column(df, col)
    if resolved is None:
        raise KeyError(f"missing_columns:[{col}]")
    col = resolved
    s = df[col]
    # Soft/descriptive filters on all-empty columns produce false zeros (e.g. ITEM_TYPE).
    if op in {"eq", "contains", "in"} and isinstance(value, str) and value.strip():
        populated = s.dropna().astype(str).str.strip()
        populated = populated[populated != ""]
        if len(populated) == 0:
            raise ValueError(f"sparse_column_unusable:{col}")
    if op == "is_null":
        return s.isna()
    if op == "not_null":
        return s.notna()
    # Identifier-style membership: compare as strings to avoid int/str mismatches.
    if op in {"eq", "ne", "in", "not_in"} and col.upper() in {
        "SKU_ID",
        "SKU_CODE",
        "TRANS_NUM",
        "STK_ID",
    }:
        s_cmp = s.astype(str)
        if isinstance(value, list):
            value = [str(v) for v in value]
        elif value is not None:
            value = str(value)
    elif op in {"contains", "not_contains", "startswith", "endswith", "regex", "eq", "ne"} and case_insensitive:
        s_cmp = s.astype(str).str.lower()
        if isinstance(value, str):
            value = value.lower()
        elif isinstance(value, list):
            value = [str(v).lower() for v in value]
    else:
        s_cmp = s

    if op == "eq":
        return s_cmp == value
    if op == "ne":
        return s_cmp != value
    if op == "in":
        return s_cmp.isin(value if isinstance(value, list) else [value])
    if op == "not_in":
        return ~s_cmp.isin(value if isinstance(value, list) else [value])
    if op == "gt":
        return pd.to_numeric(s, errors="coerce") > value
    if op == "gte":
        return pd.to_numeric(s, errors="coerce") >= value
    if op == "lt":
        return pd.to_numeric(s, errors="coerce") < value
    if op == "lte":
        return pd.to_numeric(s, errors="coerce") <= value
    if op == "between":
        lo, hi = value[0], value[1]
        num = pd.to_numeric(s, errors="coerce")
        return (num >= lo) & (num <= hi)
    if op == "contains":
        return s_cmp.astype(str).str.contains(str(value), na=False, regex=False)
    if op == "not_contains":
        return ~s_cmp.astype(str).str.contains(str(value), na=False, regex=False)
    if op == "startswith":
        return s_cmp.astype(str).str.startswith(str(value), na=False)
    if op == "endswith":
        return s_cmp.astype(str).str.endswith(str(value), na=False)
    if op == "regex":
        return s.astype(str).str.contains(str(value), na=False, regex=True)
    raise ValueError(f"unsupported_filter_op:{op}")


def _combine_masks(masks: list[pd.Series], how: str) -> pd.Series:
    if not masks:
        raise ValueError("empty_filter")
    out = masks[0]
    for m in masks[1:]:
        out = (out | m) if how == "or" else (out & m)
    return out


def op_filter_rows(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    df = handle.frame()
    clauses = args.get("clauses") or args.get("conditions") or args.get("filters")
    try:
        if clauses:
            if not isinstance(clauses, list):
                raise ValueError("clauses_must_be_list")
            how = str(args.get("combine") or "").lower()
            if how not in {"and", "or"}:
                # LLM often puts AND/OR in top-level "op" when using clauses.
                maybe = str(args.get("op") or args.get("logic") or "and").lower()
                how = maybe if maybe in {"and", "or"} else "and"
            expanded_clauses: list[dict[str, Any]] = []
            for raw_clause in clauses:
                clause = _normalize_filter_clause(raw_clause if isinstance(raw_clause, dict) else {})
                clause = dict(clause)
                clause["value"] = _expand_filter_value(ws, clause.get("value"))
                expanded_clauses.append(clause)
            masks = [_clause_mask(df, c) for c in expanded_clauses]
            mask = _combine_masks(masks, how)
        elif args.get("column") is not None or args.get("column_name") is not None:
            # Single-clause shorthand
            clause = {
                "column": args.get("column") or args.get("column_name"),
                "op": args.get("op") or args.get("operator") or "eq",
                "value": _expand_filter_value(ws, args.get("value")),
                "case_insensitive": args.get("case_insensitive", False),
            }
            mask = _clause_mask(df, clause)
        else:
            raise ValueError(
                "filter_rows_needs_clauses_or_column "
                "(use clauses/conditions:[{column,op|operator,value}] "
                "or top-level column+op+value)"
            )
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}
    out = df.loc[mask].copy()
    result = _save(ws, args.get("save_as"), out, source="filter_rows", role=handle.role)
    result["empty_after_op"] = len(out) == 0 and len(df) > 0
    result["input_row_count"] = int(len(df))
    return result


def op_sort_rows(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    by = args.get("by") or args.get("columns") or []
    if isinstance(by, str):
        by = [by]
    by = [str(c) for c in by]
    err = _require_cols(handle.frame(), by)
    if err:
        return {"error": err}
    ascending = args.get("ascending", True)
    if isinstance(ascending, list):
        asc = [bool(x) for x in ascending]
    else:
        asc = bool(ascending)
    df = handle.frame().sort_values(by=by, ascending=asc)
    return _save(ws, args.get("save_as"), df, source="sort_rows", role=handle.role)


def op_limit_rows(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    n = int(args.get("n") or 10)
    offset = int(args.get("offset") or 0)
    df = handle.frame().iloc[offset : offset + n].copy()
    return _save(ws, args.get("save_as"), df, source="limit_rows", role=handle.role)


def op_distinct_rows(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    subset = args.get("columns")
    df = handle.frame().drop_duplicates(subset=subset if subset else None)
    return _save(ws, args.get("save_as"), df, source="distinct_rows", role=handle.role)


def op_drop_duplicates(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    return op_distinct_rows(ws, args, out_dir)


# ----- D. Aggregate -----

_AGG_MAP = {
    "sum": "sum",
    "mean": "mean",
    "avg": "mean",
    "count": "count",
    "nunique": "nunique",
    "min": "min",
    "max": "max",
    "median": "median",
    "std": "std",
}


def _normalize_groupby_aggs(raw: Any) -> list[dict[str, str]] | dict[str, Any]:
    """Accept common LLM shapes for groupby aggs.

    Supported:
      - [{"column": "QTY", "fn": "sum", "as": "qty_sum"}]
      - [{"column": "QTY", "func": "sum", "new_column_name": "qty_sum"}]
      - {"qty_sum": ["QTY", "sum"]} / {"qty_sum": {"column": "QTY", "fn": "sum"}}
      - [["QTY", "sum"], ["QTY", "sum", "qty_sum"]]
    """
    if raw is None:
        return []
    if isinstance(raw, dict):
        out: list[dict[str, str]] = []
        for key, value in raw.items():
            if isinstance(value, dict):
                col = str(value.get("column") or value.get("col") or "").strip()
                fn = str(value.get("fn") or value.get("func") or value.get("agg") or "sum")
                if not col:
                    return {"error": f"agg_missing_column:{key}"}
                out.append({"column": col, "fn": fn, "as": str(key)})
            elif isinstance(value, (list, tuple)) and len(value) >= 2:
                out.append({"column": str(value[0]), "fn": str(value[1]), "as": str(key)})
            else:
                return {"error": f"unsupported_agg_shape:{key}"}
        return out
    if not isinstance(raw, list):
        return {"error": "aggs_must_be_list_or_dict"}
    out = []
    for item in raw:
        if isinstance(item, dict):
            col = str(
                item.get("column")
                or item.get("col")
                or item.get("field")
                or ""
            ).strip()
            if not col:
                return {"error": "agg_missing_column"}
            fn = str(
                item.get("fn")
                or item.get("func")
                or item.get("agg")
                or item.get("aggregation")
                or "sum"
            )
            alias = str(
                item.get("as")
                or item.get("new_column_name")
                or item.get("name")
                or item.get("alias")
                or f"{col}_{fn}"
            )
            out.append({"column": col, "fn": fn, "as": alias})
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            col = str(item[0])
            fn = str(item[1])
            alias = str(item[2]) if len(item) >= 3 else f"{col}_{fn}"
            out.append({"column": col, "fn": fn, "as": alias})
        else:
            return {"error": f"unsupported_agg_item:{type(item).__name__}"}
    return out


_NUMERIC_AGGS = frozenset({"sum", "mean", "median", "std", "min", "max"})


def op_groupby_agg(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    by = [str(c) for c in (args.get("by") or [])]
    normalized = _normalize_groupby_aggs(args.get("aggs"))
    if isinstance(normalized, dict) and normalized.get("error"):
        return normalized
    aggs = list(normalized or [])
    err = _require_cols(handle.frame(), by + [str(a["column"]) for a in aggs if a.get("column")])
    if err:
        return {"error": err}
    named: dict[str, tuple[str, str]] = {}
    for a in aggs:
        col = str(a["column"])
        fn = str(a.get("fn") or "sum").lower()
        if fn not in _AGG_MAP:
            return {"error": f"unsupported_agg:{fn}"}
        out_name = str(a.get("as") or f"{col}_{fn}")
        named[out_name] = (col, _AGG_MAP[fn])
    if not named:
        return {"error": "aggs_required"}
    df = handle.frame().copy()
    for col, fn in named.values():
        if fn in _NUMERIC_AGGS:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if not by:
        # Global aggregate (LLM often passes empty group_by for a single total).
        row = {out: getattr(df[col], fn)() for out, (col, fn) in named.items()}
        grouped = pd.DataFrame([row])
    else:
        grouped = df.groupby(by, dropna=False).agg(**{k: v for k, v in named.items()})
        grouped = grouped.reset_index()
    return _save(ws, args.get("save_as"), grouped, source="groupby_agg", role="aggregate")


def op_pivot_table(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    index = args.get("index")
    columns = args.get("columns")
    values = args.get("values")
    aggfunc = str(args.get("aggfunc") or "sum")
    try:
        piv = pd.pivot_table(
            handle.frame(),
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=args.get("fill_value"),
        ).reset_index()
        piv.columns = [str(c) if not isinstance(c, tuple) else "_".join(str(x) for x in c) for c in piv.columns]
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}
    return _save(ws, args.get("save_as"), piv, source="pivot_table", role="aggregate")


def op_melt(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    id_vars = args.get("id_vars")
    value_vars = args.get("value_vars")
    try:
        melted = handle.frame().melt(
            id_vars=id_vars,
            value_vars=value_vars,
            var_name=args.get("var_name") or "variable",
            value_name=args.get("value_name") or "value",
        )
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}
    return _save(ws, args.get("save_as"), melted, source="melt", role=handle.role)


def op_window_rank(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    partition_by = _as_col_list(args.get("partition_by"))
    order_by, order_asc = _as_order_by(args.get("order_by"), default_ascending=args.get("ascending", False))
    ascending = order_asc if isinstance(order_asc, list) else args.get("ascending", False)
    method = str(args.get("method") or "row_number").lower()
    rank_col = str(args.get("rank_column") or "rn")
    err = _require_cols(handle.frame(), partition_by + order_by)
    if err:
        return {"error": err}
    if isinstance(ascending, list):
        asc_list = [bool(x) for x in ascending]
    else:
        asc_list = [bool(ascending)] * max(len(order_by), 1)
    df = handle.frame().copy()
    sort_keys = partition_by + order_by
    sort_asc = [True] * len(partition_by) + asc_list[: len(order_by)]
    if sort_keys:
        df = df.sort_values(by=sort_keys, ascending=sort_asc)
    if method == "row_number":
        if partition_by:
            df[rank_col] = df.groupby(partition_by, dropna=False).cumcount() + 1
        else:
            df[rank_col] = range(1, len(df) + 1)
    else:
        rank_method = "min" if method == "rank" else "dense"
        asc0 = bool(asc_list[0]) if asc_list else False
        if partition_by:
            df[rank_col] = df.groupby(partition_by, dropna=False)[order_by[0]].rank(
                method=rank_method, ascending=asc0
            )
        else:
            df[rank_col] = df[order_by[0]].rank(method=rank_method, ascending=asc0)
    return _save(ws, args.get("save_as"), df, source="window_rank", role=handle.role)


def op_top_n_per_group(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    # Prefer explicit partition_by (including []) for global top-N; else group_by.
    if "partition_by" in args:
        partition_by = _as_col_list(args.get("partition_by"))
    else:
        partition_by = _as_col_list(args.get("group_by"))
    order_by, order_asc = _as_order_by(args.get("order_by"), default_ascending=args.get("ascending", False))
    n = int(args.get("n") or 5)
    ascending = order_asc if isinstance(order_asc, list) else args.get("ascending", False)
    err = _require_cols(handle.frame(), partition_by + order_by)
    if err:
        return {"error": err}
    if isinstance(ascending, list):
        asc = [bool(x) for x in ascending]
    else:
        asc = [bool(ascending)] * max(len(order_by), 1)
    df = handle.frame()
    if not partition_by:
        # Global top-N (e.g. 5 most recent bills).
        sort_cols = order_by or list(df.columns[:1])
        if isinstance(ascending, list):
            asc_g = [bool(x) for x in ascending][: len(sort_cols)]
            if len(asc_g) < len(sort_cols):
                asc_g = asc_g + [bool(ascending[-1] if ascending else False)] * (len(sort_cols) - len(asc_g))
        else:
            asc_g = [bool(ascending)] * len(sort_cols)
        out = df.sort_values(by=sort_cols, ascending=asc_g).head(n).copy()
        return _save(ws, args.get("save_as"), out, source="top_n_per_group", role=handle.role)
    df = df.sort_values(by=partition_by + order_by, ascending=[True] * len(partition_by) + asc)
    df = df.copy()
    df["_rn"] = df.groupby(partition_by, dropna=False).cumcount() + 1
    out = df.loc[df["_rn"] <= n].drop(columns=["_rn"])
    return _save(ws, args.get("save_as"), out, source="top_n_per_group", role=handle.role)


def op_percent_of_total(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    col = str(args["column"])
    out_col = str(args.get("as") or f"{col}_pct")
    group_by = _as_col_list(args.get("group_by"))
    err = _require_cols(handle.frame(), [col] + group_by)
    if err:
        return {"error": err}
    df = handle.frame().copy()
    num = pd.to_numeric(df[col], errors="coerce")
    if group_by:
        total = num.groupby([df[c] for c in group_by]).transform("sum")
    else:
        total = num.sum()
    df[out_col] = num / total.replace(0, pd.NA)
    return _save(ws, args.get("save_as"), df, source="percent_of_total", role=handle.role)


def op_cumulative_sum(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    col = str(args["column"])
    out_col = str(args.get("as") or f"{col}_cumsum")
    group_by = _as_col_list(args.get("group_by"))
    err = _require_cols(handle.frame(), [col] + group_by)
    if err:
        return {"error": err}
    df = handle.frame().copy()
    num = pd.to_numeric(df[col], errors="coerce")
    if group_by:
        df[out_col] = num.groupby([df[c] for c in group_by]).cumsum()
    else:
        df[out_col] = num.cumsum()
    return _save(ws, args.get("save_as"), df, source="cumulative_sum", role=handle.role)


# ----- E. Join -----


def op_join_datasets(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    left = ws.get(str(args["left"])).frame()
    right = ws.get(str(args["right"])).frame()
    how = str(args.get("how") or "left")
    on = args.get("on")
    left_on = args.get("left_on")
    right_on = args.get("right_on")
    suffixes = args.get("suffixes")
    if not suffixes:
        suffixes = _default_join_suffixes(left, right)
    else:
        suffixes = tuple(suffixes)
    try:
        if on:
            merged = left.merge(right, how=how, on=on, suffixes=suffixes)
        else:
            merged = left.merge(
                right,
                how=how,
                left_on=left_on,
                right_on=right_on,
                suffixes=suffixes,
            )
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}
    return _save(ws, args.get("save_as"), merged, source="join_datasets")


def op_concat_datasets(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    refs = [str(r) for r in (args.get("datasets") or [])]
    frames = [ws.get(r).frame() for r in refs]
    keys = args.get("keys")
    try:
        if keys:
            out = pd.concat(frames, keys=keys, ignore_index=False).reset_index(level=0).rename(columns={"level_0": "source"})
        else:
            out = pd.concat(frames, ignore_index=True)
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}
    return _save(ws, args.get("save_as"), out, source="concat_datasets")


def op_set_compare(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    left = ws.get(str(args["left"])).frame()
    right = ws.get(str(args["right"])).frame()
    on = args.get("on") or args.get("columns")
    if isinstance(on, str):
        on = [on]
    on = [str(c) for c in (on or [])]
    mode = str(args.get("mode") or "left_only")  # left_only | right_only | both
    err = _require_cols(left, on) or _require_cols(right, on)
    if err:
        return {"error": err}
    merged = left.merge(right[on].drop_duplicates(), on=on, how="left", indicator=True)
    if mode == "left_only":
        out = merged.loc[merged["_merge"] == "left_only"].drop(columns=["_merge"])
    elif mode == "right_only":
        merged_r = right.merge(left[on].drop_duplicates(), on=on, how="left", indicator=True)
        out = merged_r.loc[merged_r["_merge"] == "left_only"].drop(columns=["_merge"])
    else:
        out = merged.loc[merged["_merge"] == "both"].drop(columns=["_merge"])
    return _save(ws, args.get("save_as"), out, source="set_compare")


# ----- E2. Source / artifact lifecycle -----


def op_load_tabular(
    ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path
) -> dict[str, Any]:
    source_ref = str(args["source_ref"])
    save_as = str(args.get("save_as") or f"{source_ref}_loaded")
    source = ws.sources.get(source_ref) or (
        ws.get(source_ref) if ws.has(source_ref) else None
    )
    if source is None or not source.path:
        return {"error": f"unknown_source:{source_ref}"}
    frame = read_tabular(
        source.path,
        format=args.get("format") or source.format,
        sheet_name=args.get("sheet_name") or source.sheet_name,
    )
    handle = ws.save_frame(
        save_as,
        frame,
        role=source.role,
        purpose=source.purpose,
        source=source_ref,
        parents=[source_ref],
        op_id="load_tabular",
        op_args={k: v for k, v in args.items() if k != "path"},
    )
    return {
        "saved_as": handle.ref,
        "row_count": len(frame),
        "columns": [str(c) for c in frame.columns],
    }


def op_reload_artifact(
    ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path
) -> dict[str, Any]:
    artifact = ws.get_artifact(str(args["artifact_id"]))
    if artifact.validation_status == "invalid":
        return {"error": "artifact_invalid"}
    frame = read_tabular(
        artifact.path,
        sheet_name=args.get("sheet_name"),
    )
    save_as = str(args.get("save_as") or f"artifact_{artifact.artifact_id[:8]}")
    handle = ws.save_frame(
        save_as,
        frame,
        source=artifact.artifact_id,
        parents=[artifact.artifact_id],
        op_id="reload_artifact",
        op_args={"sheet_name": args.get("sheet_name")},
    )
    return {
        "saved_as": handle.ref,
        "row_count": len(frame),
        "columns": [str(c) for c in frame.columns],
        "artifact_id": artifact.artifact_id,
    }


def op_inspect_excel(
    ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path
) -> dict[str, Any]:
    if args.get("artifact_id"):
        path = ws.get_artifact(str(args["artifact_id"])).path
    else:
        source_ref = str(args["source_ref"])
        source = ws.sources.get(source_ref) or ws.get(source_ref)
        if not source.path:
            return {"error": "source_has_no_path"}
        path = source.path
    if Path(path).suffix.lower() != ".xlsx":
        return {"error": "not_xlsx"}
    return inspect_workbook(path, sample_rows=int(args.get("sample_rows", 5)))


def op_validate_export(
    ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path
) -> dict[str, Any]:
    artifact = ws.get_artifact(str(args["artifact_id"]))
    issues: list[str] = []
    path = Path(artifact.path)
    try:
        path.resolve().relative_to(out_dir.resolve())
    except ValueError:
        issues.append("outside_output_root")
    if not path.exists() or not path.is_file() or path.is_symlink():
        issues.append("missing_or_unsafe_file")
    elif path.stat().st_size <= 0:
        issues.append("empty_file")
    elif sha256_file(path) != artifact.sha256:
        issues.append("checksum_mismatch")

    inspection: dict[str, Any] = {}
    if not issues:
        try:
            if path.suffix.lower() == ".xlsx":
                inspection = inspect_workbook(path)
            elif path.suffix.lower() in {".csv", ".parquet"}:
                inspection = inspect_tabular(path)
            else:
                inspection = {"format": path.suffix.lstrip(".").lower()}
        except Exception as exc:  # noqa: BLE001
            issues.append(f"unreadable:{exc}")

    expected = args.get("expected_dataset")
    if expected and not issues:
        source = ws.get(str(expected)).frame()
        if path.suffix.lower() == ".xlsx":
            sheet_name = args.get("sheet_name") or (
                inspection.get("sheet_names") or ["data"]
            )[0]
            loaded = read_tabular(path, sheet_name=sheet_name)
        else:
            loaded = read_tabular(path)
        if len(source) != len(loaded):
            issues.append(f"row_count_mismatch:{len(source)}!={len(loaded)}")
        if [str(c) for c in source.columns] != [str(c) for c in loaded.columns]:
            issues.append("columns_mismatch")

    artifact.validation_status = "valid" if not issues else "invalid"
    artifact.validation_issues = issues
    return {
        "artifact_id": artifact.artifact_id,
        "valid": not issues,
        "issues": issues,
        "inspection": inspection,
        **({"error": "artifact_validation_failed"} if issues else {}),
    }


def op_compare_datasets(
    ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path
) -> dict[str, Any]:
    left = ws.get(str(args["left"])).frame()
    right = ws.get(str(args["right"])).frame()
    keys = [str(k) for k in (args.get("keys") or [])]
    tolerance = float(args.get("numeric_tolerance", 0.0))
    issues: dict[str, Any] = {
        "row_count_delta": len(right) - len(left),
        "left_only_columns": [str(c) for c in left.columns if c not in right.columns],
        "right_only_columns": [str(c) for c in right.columns if c not in left.columns],
    }
    common = [str(c) for c in left.columns if c in right.columns]
    mismatch_counts: dict[str, int] = {}
    diff_rows = pd.DataFrame()
    if keys:
        err = _require_cols(left, keys) or _require_cols(right, keys)
        if err:
            return {"error": err}
        if left.duplicated(keys).any() or right.duplicated(keys).any():
            return {"error": "duplicate_comparison_keys"}
        merged = left.merge(right, on=keys, how="outer", suffixes=("_left", "_right"), indicator=True)
        for column in [c for c in common if c not in keys]:
            lcol, rcol = f"{column}_left", f"{column}_right"
            if pd.api.types.is_numeric_dtype(left[column]) and pd.api.types.is_numeric_dtype(right[column]):
                mismatch = ~np.isclose(
                    pd.to_numeric(merged[lcol], errors="coerce"),
                    pd.to_numeric(merged[rcol], errors="coerce"),
                    atol=tolerance,
                    rtol=0,
                    equal_nan=True,
                )
            else:
                mismatch = merged[lcol].fillna("<NULL>").astype(str) != merged[rcol].fillna("<NULL>").astype(str)
            mismatch_counts[column] = int(mismatch.sum())
        diff_rows = merged.loc[
            (merged["_merge"] != "both")
            | pd.Series(False, index=merged.index)
        ]
    else:
        left_hash = pd.util.hash_pandas_object(left[common], index=False).value_counts()
        right_hash = pd.util.hash_pandas_object(right[common], index=False).value_counts()
        issues["row_hash_multiset_equal"] = left_hash.equals(right_hash)
    issues["mismatch_counts"] = mismatch_counts
    equal = (
        issues["row_count_delta"] == 0
        and not issues["left_only_columns"]
        and not issues["right_only_columns"]
        and not any(mismatch_counts.values())
        and issues.get("row_hash_multiset_equal", True)
    )
    result = {"equal": equal, **issues}
    if args.get("save_as") and not diff_rows.empty:
        result.update(_save(ws, str(args["save_as"]), diff_rows, source="compare_datasets"))
    return result


def op_get_lineage(
    ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path
) -> dict[str, Any]:
    ref = str(args.get("ref") or args.get("dataset") or args.get("artifact_id"))
    node = ws.lineage.get(ref)
    if node is None:
        return {"error": f"lineage_not_found:{ref}"}
    nodes = [node.model_dump()]
    if bool(args.get("recursive", True)):
        pending = list(node.parents)
        seen = {node.node_id}
        while pending:
            parent = pending.pop(0)
            if parent in seen:
                continue
            seen.add(parent)
            parent_node = ws.lineage.get(parent)
            if parent_node:
                nodes.append(parent_node.model_dump())
                pending.extend(parent_node.parents)
    return {"nodes": nodes}


# ----- F. Export -----


def _safe_filename(name: str, suffix: str) -> str:
    value = Path(name).name
    if value != name or name in {"", ".", ".."} or "/" in name or "\\" in name:
        raise ValueError("unsafe_filename")
    value = re.sub(r"[^A-Za-z0-9_. -]", "_", value)[:120]
    if not value.lower().endswith(suffix):
        value += suffix
    return value


def _atomic_target(out_dir: Path, filename: str) -> tuple[Path, Path]:
    out = out_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    target = (out / filename).resolve()
    try:
        target.relative_to(out)
    except ValueError as exc:
        raise ValueError("output_path_not_allowed") from exc
    temp = target.with_name(
        f".{target.stem}.{os.getpid()}.tmp{target.suffix}"
    )
    return target, temp


def op_export_csv(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    name = _safe_filename(str(args.get("filename") or f"{handle.ref}.csv"), ".csv")
    path, temp = _atomic_target(out_dir, name)
    frame = neutralize_spreadsheet_formulas(handle.frame())
    frame.to_csv(temp, index=False)
    temp.replace(path)
    primary = bool(args.get("primary", True))
    record = ws.register_artifact(
        str(path),
        kind="csv",
        primary=primary,
        source_refs=[handle.ref],
        metadata={"row_count": len(frame), "columns": [str(c) for c in frame.columns]},
        validated=True,
    )
    return {
        "path": str(path),
        "artifact_id": record.artifact_id,
        "row_count": int(len(frame)),
        "columns": [str(c) for c in frame.columns],
        "artifact": True,
        "sha256": record.sha256,
    }


def op_export_excel(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    sheets = args.get("sheets")  # {sheet_name: dataset_ref}
    name = _safe_filename(str(args.get("filename") or "analysis.xlsx"), ".xlsx")
    path, temp = _atomic_target(out_dir, name)
    source_refs: list[str] = []
    try:
        with pd.ExcelWriter(temp, engine="openpyxl") as writer:
            if sheets:
                for sheet, ref in sheets.items():
                    source_refs.append(str(ref))
                    neutralize_spreadsheet_formulas(ws.get(str(ref)).frame()).to_excel(
                        writer, sheet_name=str(sheet)[:31], index=False
                    )
            else:
                ref = str(args["dataset"])
                source_refs.append(ref)
                neutralize_spreadsheet_formulas(ws.get(ref).frame()).to_excel(
                    writer, sheet_name="data", index=False
                )
        temp.replace(path)
    except Exception as exc:  # noqa: BLE001
        temp.unlink(missing_ok=True)
        return {"error": str(exc)}
    inspection = inspect_workbook(path)
    record = ws.register_artifact(
        str(path),
        kind="excel",
        primary=bool(args.get("primary", True)),
        source_refs=source_refs,
        sheet_map={str(k): str(v) for k, v in (sheets or {"data": source_refs[0]}).items()},
        metadata=inspection,
        validated=True,
    )
    return {
        "path": str(path),
        "artifact_id": record.artifact_id,
        "artifact": True,
        "kind": "excel",
        "sheets": inspection["sheet_names"],
        "sha256": record.sha256,
    }


def op_plot_chart(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    handle = ws.get(str(args["dataset"]))
    df = handle.frame()
    x = str(args["x"])
    y = str(args["y"])
    kind = str(args.get("kind") or "bar").lower()
    title = str(args.get("title") or "")
    hue = str(args.get("hue") or "")
    err = _require_cols(df, [x, y])
    if err:
        return {"error": err}
    if kind not in {"bar", "line", "pie", "hist"}:
        return {"error": f"unsupported_chart_kind:{kind}"}
    if hue and hue not in df.columns:
        return {"error": f"missing_columns:['{hue}']"}
    numeric_y = pd.to_numeric(df[y], errors="coerce")
    if numeric_y.notna().sum() == 0:
        return {"error": f"non_numeric_y:{y}"}
    if kind == "pie" and ((numeric_y.dropna() < 0).any() or numeric_y.fillna(0).sum() <= 0):
        return {"error": "invalid_pie_values"}
    name = _safe_filename(
        str(args.get("filename") or f"{handle.ref}_{kind}.png"), ".png"
    )
    path, temp = _atomic_target(out_dir, name)
    figsize = args.get("figsize") or [10, 6]
    if not isinstance(figsize, list) or len(figsize) != 2:
        figsize = [10, 6]
    plt.figure(figsize=(float(figsize[0]), float(figsize[1])))
    try:
        if hue and kind in {"bar", "line"}:
            pivot = df.assign(_y=numeric_y).pivot_table(
                index=x, columns=hue, values="_y", aggfunc="sum"
            )
            pivot.plot(kind=kind, ax=plt.gca())
        elif kind == "bar":
            plt.bar(df[x].astype(str), numeric_y)
        elif kind == "line":
            plt.plot(df[x].astype(str), numeric_y)
        elif kind == "pie":
            plt.pie(numeric_y.fillna(0), labels=df[x].astype(str), autopct="%1.1f%%")
        elif kind == "hist":
            plt.hist(numeric_y.dropna())
        if title:
            plt.title(title)
        if kind != "pie":
            plt.xlabel(str(args.get("x_label") or x))
            plt.ylabel(str(args.get("y_label") or y))
        rotation = int(args.get("rotate_x_labels", 0) or 0)
        if rotation:
            plt.xticks(rotation=max(-90, min(rotation, 90)))
        plt.tight_layout()
        plt.savefig(temp)
        temp.replace(path)
    finally:
        plt.close()
        temp.unlink(missing_ok=True)
    from project_core.domain.analysis.chart_validation import (
        source_data_fingerprint,
        validate_chart_artifact,
    )

    chart_columns = [x, y] + ([hue] if hue else [])
    chart_source = df[chart_columns]
    fingerprint = source_data_fingerprint(chart_source)
    validation = validate_chart_artifact(
        path,
        allowed_root=out_dir,
        source_data=chart_source,
        expected_source_fingerprint=fingerprint,
    )
    if validation.verdict != "pass":
        path.unlink(missing_ok=True)
        return {"error": "chart_validation_failed", "issues": validation.issues}
    record = ws.register_artifact(
        str(path),
        kind="chart",
        primary=bool(args.get("primary", True)),
        source_refs=[handle.ref],
        metadata={
            "chart_spec": {"kind": kind, "x": x, "y": y, "hue": hue or None, "title": title},
            "row_count": len(df),
            "columns": [str(c) for c in df.columns],
            "validation": validation.model_dump(),
        },
        validated=True,
    )
    return {
        "path": str(path),
        "artifact_id": record.artifact_id,
        "artifact": True,
        "kind": "chart",
        "validation": validation.model_dump(),
    }


def op_bundle_deliverables(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    artifact_ids = [str(p) for p in (args.get("artifact_ids") or [])]
    for path in args.get("paths") or []:
        record = ws.artifact_for_path(str(path))
        if record is None:
            return {"error": f"unregistered_artifact:{Path(str(path)).name}"}
        artifact_ids.append(record.artifact_id)
    artifact_ids = list(dict.fromkeys(artifact_ids))
    for artifact_id in artifact_ids:
        record = ws.get_artifact(artifact_id)
        record.primary = True
        if record.path not in ws.primary_artifacts:
            ws.primary_artifacts.append(record.path)
    if not artifact_ids:
        # Mark all current artifacts as primary
        for record in ws.artifacts.values():
            record.primary = True
            if record.path not in ws.primary_artifacts:
                ws.primary_artifacts.append(record.path)
    return {
        "primary_artifacts": list(ws.primary_artifacts),
        "artifact_ids": [a.artifact_id for a in ws.artifacts.values() if a.primary],
    }


# ----- G. Critic -----


def op_match_brief_coverage(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    brief = args.get("brief") or {}
    requirements = [
        item
        for item in (brief.get("requirements") or [])
        if isinstance(item, dict)
        and item.get("source") == "explicit"
        and bool(item.get("required", True))
    ]
    if requirements:
        metrics = [
            str(item.get("key") or "").lower()
            for item in requirements
            if item.get("kind") == "metric"
        ]
        dimensions = [
            str(item.get("key") or "").lower()
            for item in requirements
            if item.get("kind") == "dimension"
        ]
        filter_values = {
            str(item.get("key") or "").lower(): item.get("value")
            for item in requirements
            if item.get("kind") == "filter"
        }
        time_requirements = [
            item for item in requirements if item.get("kind") == "time"
        ]
        ranking_requirements = [
            item for item in requirements if item.get("kind") == "ranking"
        ]
        time_range = (
            dict(time_requirements[0].get("value") or {})
            if time_requirements
            else {}
        )
    else:
        metrics = [str(m).lower() for m in (brief.get("metrics") or [])]
        dimensions = [str(d).lower() for d in (brief.get("dimensions") or [])]
        filter_values = {
            str(key).lower(): value for key, value in (brief.get("filters") or {}).items()
        }
        time_range = brief.get("time_range") or {}
        ranking_requirements = []
    filters = [str(k).lower() for k in filter_values]
    all_cols: set[str] = set()
    total_rows = 0
    frames: list[pd.DataFrame] = []
    for prof in ws.list_profiles():
        if prof.get("error"):
            continue
        all_cols.update(str(c).lower() for c in (prof.get("columns") or []))
        total_rows += int(prof.get("row_count") or 0)
        ref = str(prof.get("ref") or "")
        if ref and ws.has(ref):
            try:
                frames.append(ws.get(ref).frame())
            except Exception:  # noqa: BLE001
                pass

    semantic_labels: list[str] = []
    for item in args.get("semantic_labels") or []:
        if isinstance(item, str):
            semantic_labels.append(item)
        elif isinstance(item, dict):
            semantic_labels.extend(
                str(value)
                for key, value in item.items()
                if key in {"output_name", "semantic_key", "purpose"}
                and value
            )
            source = item.get("source") or {}
            semantic_labels.extend(
                str(value) for value in (source.get("physical_columns") or []) if value
            )

    synonyms = {
        "qty": "quantity",
        "quantity": "quantity",
        "sku": "product",
        "product": "product",
        "item": "product",
        "plu": "product",
        "trans": "transaction",
        "tran": "transaction",
        "transaction": "transaction",
        "bill": "transaction",
        "invoice": "transaction",
        "receipt": "transaction",
        "amount": "amount",
        "value": "amount",
        "revenue": "amount",
        "sales": "amount",
        "code": "code",
        "category": "category",
        "group": "category",
        "grp": "category",
        "date": "time",
        "time": "time",
        "day": "time",
        "month": "time",
        "year": "time",
    }

    def _tokens(value: str) -> set[str]:
        expanded = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", value)
        raw = re.findall(r"[a-z0-9]+", expanded.lower())
        out: set[str] = set()
        for token in raw:
            if token in {"min", "max", "total", "minimum", "maximum"}:
                continue
            mapped = synonyms.get(token)
            if mapped:
                out.add(mapped)
                continue
            for prefix, canonical in synonyms.items():
                if len(prefix) >= 4 and token.startswith(prefix):
                    out.add(canonical)
                    break
            else:
                out.add(token)
        return out

    evidence_labels = sorted(all_cols) + semantic_labels
    evidence_tokens = [_tokens(label) for label in evidence_labels]

    def _present(names: list[str]) -> tuple[list[str], list[str]]:
        found, missing = [], []
        for n in names:
            needed = _tokens(n)
            if any(
                n in label.lower()
                or label.lower() in n
                or (needed and needed.issubset(tokens))
                for label, tokens in zip(evidence_labels, evidence_tokens, strict=True)
            ):
                found.append(n)
            else:
                missing.append(n)
        return found, missing

    m_found, m_missing = _present(metrics)
    d_found, d_missing = _present(dimensions)
    f_found: list[str] = []
    f_missing: list[str] = []

    def _normalize_code(value: Any) -> str:
        text = re.sub(r"\D", "", str(value))
        return text.lstrip("0") or "0"

    def _norm_scalar(value: Any) -> str:
        return re.sub(r"\s+", " ", str(value).strip().lower())

    def _filter_has_value_evidence(name: str, expected: Any) -> bool:
        needed = _tokens(name)
        if not frames:
            return False
        if "product" in needed:
            values = expected if isinstance(expected, list) else [expected]
            wanted = {_normalize_code(value) for value in values}
            seen: set[str] = set()
            for frame in frames:
                for column in frame.columns:
                    column_tokens = _tokens(str(column))
                    if "product" not in column_tokens:
                        continue
                    seen.update(
                        _normalize_code(value)
                        for value in frame[column].dropna().astype(str).head(5_000)
                    )
            return bool(wanted) and wanted.issubset(seen)
        if "amount" in needed and isinstance(expected, (int, float)):
            for frame in frames:
                for column in frame.columns:
                    column_tokens = _tokens(str(column))
                    if "amount" not in column_tokens:
                        continue
                    numeric = pd.to_numeric(frame[column], errors="coerce").dropna()
                    if not numeric.empty and bool((numeric >= float(expected)).all()):
                        return True
            return False
        if "category" in needed:
            wanted = str(expected).strip().lower()
            if not wanted:
                return False
            for frame in frames:
                for column in frame.columns:
                    if "category" not in _tokens(str(column)):
                        continue
                    if frame[column].dropna().astype(str).str.lower().str.contains(
                        re.escape(wanted), regex=True
                    ).any():
                        return True
            return False
        expected_values = expected if isinstance(expected, list) else [expected]
        wanted = {_norm_scalar(value) for value in expected_values}
        seen: set[str] = set()
        for frame in frames:
            for column in frame.columns:
                column_tokens = _tokens(str(column))
                if not (needed & column_tokens) and name not in str(column).lower():
                    continue
                seen.update(
                    _norm_scalar(value)
                    for value in frame[column].dropna().astype(str).head(5_000)
                )
        return bool(wanted) and wanted.issubset(seen)

    for name in filters:
        if _filter_has_value_evidence(name, filter_values.get(name)):
            f_found.append(name)
        else:
            f_missing.append(name)

    needs_time = bool(time_range.get("start") or time_range.get("end") or time_range.get("grain"))
    time_columns = [label for label, tokens in zip(evidence_labels, evidence_tokens, strict=True) if "time" in tokens]
    time_ok = not needs_time
    if needs_time:
        start = pd.to_datetime(time_range.get("start"), errors="coerce")
        end = pd.to_datetime(time_range.get("end"), errors="coerce")
        raw_end = str(time_range.get("end") or "")
        if not pd.isna(end) and "T" not in raw_end and " " not in raw_end:
            end = end + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
        for frame in frames:
            for column in frame.columns:
                if "time" not in _tokens(str(column)):
                    continue
                values = pd.to_datetime(frame[column], errors="coerce").dropna()
                if values.empty:
                    continue
                after_start = True if pd.isna(start) else bool((values >= start).all())
                before_end = True if pd.isna(end) else bool((values <= end).all())
                if after_start and before_end:
                    time_ok = True
                    break
            if time_ok:
                break

    ranking_found: list[str] = []
    ranking_missing: list[str] = []
    for item in ranking_requirements:
        requirement_id = str(item.get("requirement_id") or item.get("key") or "ranking")
        value = item.get("value") or {}
        limit = int(value.get("limit") or 0) if isinstance(value, dict) else 0
        partition_key = str(value.get("partition_by") or "") if isinstance(value, dict) else ""
        order_key = str(value.get("order_by") or "") if isinstance(value, dict) else ""
        direction = str(value.get("direction") or "desc").lower() if isinstance(value, dict) else "desc"
        passed = False
        if limit > 0:
            partition_tokens = _tokens(partition_key)
            order_tokens = _tokens(order_key)
            for frame in frames:
                partition_columns = [
                    str(column)
                    for column in frame.columns
                    if partition_tokens and partition_tokens.issubset(_tokens(str(column)))
                ]
                order_columns = [
                    str(column)
                    for column in frame.columns
                    if order_tokens and order_tokens.issubset(_tokens(str(column)))
                ]
                if not order_columns:
                    continue
                partition_column = partition_columns[0] if partition_columns else None
                groups = (
                    [group for _, group in frame.groupby(partition_column, dropna=False)]
                    if partition_column
                    else [frame]
                )
                if not groups or any(len(group) > limit for group in groups):
                    continue
                ordered = True
                for group in groups:
                    comparable = group[order_columns].dropna()
                    if comparable.empty:
                        ordered = False
                        break
                    expected_order = comparable.sort_values(
                        by=order_columns,
                        ascending=direction != "desc",
                        kind="stable",
                    )
                    if list(comparable.index) != list(expected_order.index):
                        ordered = False
                        break
                if ordered:
                    passed = True
                    break
        if passed:
            ranking_found.append(requirement_id)
        else:
            ranking_missing.append(requirement_id)

    ok = (
        total_rows > 0
        and not m_missing
        and not d_missing
        and not f_missing
        and time_ok
        and not ranking_missing
    )
    return {
        "ok": ok,
        "total_rows": total_rows,
        "columns": sorted(all_cols),
        "metrics_found": m_found,
        "metrics_missing": m_missing,
        "dimensions_found": d_found,
        "dimensions_missing": d_missing,
        "filters_found": f_found,
        "filters_missing": f_missing,
        "time_required": needs_time,
        "time_columns": sorted(time_columns),
        "time_covered": time_ok,
        "ranking_found": ranking_found,
        "ranking_missing": ranking_missing,
        "issue": None if ok else ("empty_result" if total_rows <= 0 else "insufficient_deliverable"),
    }


def op_detect_empty_after_filter(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    ref = str(args["dataset"])
    handle = ws.get(ref)
    df = handle.frame()
    empty = len(df) == 0
    return {
        "dataset": ref,
        "empty": empty,
        "row_count": int(len(df)),
        "issue": "empty_result" if empty else None,
        "hint": "filter_too_strict_or_wrong_sql" if empty else None,
    }


def op_grain_check(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    key = [str(c) for c in (args.get("key") or [])]
    expected = str(args.get("expected_grain") or "any")  # one_row_per_key | many | any
    err = _require_cols(handle.frame(), key) if key else None
    if err:
        return {"error": err}
    df = handle.frame()
    if not key:
        return {"dataset": args["dataset"], "row_count": int(len(df)), "grain": "ungrouped", "ok": True}
    counts = df.groupby(key, dropna=False).size()
    max_per = int(counts.max()) if len(counts) else 0
    one = max_per <= 1
    if expected == "one_row_per_key":
        ok = one
    elif expected == "many":
        ok = max_per > 1
    else:
        ok = True
    return {
        "dataset": args["dataset"],
        "ok": ok,
        "n_keys": int(len(counts)),
        "max_rows_per_key": max_per,
        "is_one_row_per_key": one,
        "issue": None if ok else "grain",
    }


HANDLERS: dict[str, OpHandler] = {
    "list_datasets": op_list_datasets,
    "describe_columns": op_describe_columns,
    "head_rows": op_head_rows,
    "sample_rows": op_sample_rows,
    "value_counts": op_value_counts,
    "null_report": op_null_report,
    "assert_nonempty": op_assert_nonempty,
    "assert_columns_present": op_assert_columns_present,
    "select_columns": op_select_columns,
    "rename_columns": op_rename_columns,
    "drop_columns": op_drop_columns,
    "cast_column": op_cast_column,
    "add_column_expr": op_add_column_expr,
    "fill_null": op_fill_null,
    "drop_null": op_drop_null,
    "filter_rows": op_filter_rows,
    "sort_rows": op_sort_rows,
    "limit_rows": op_limit_rows,
    "distinct_rows": op_distinct_rows,
    "drop_duplicates": op_drop_duplicates,
    "groupby_agg": op_groupby_agg,
    "pivot_table": op_pivot_table,
    "melt": op_melt,
    "window_rank": op_window_rank,
    "top_n_per_group": op_top_n_per_group,
    "percent_of_total": op_percent_of_total,
    "cumulative_sum": op_cumulative_sum,
    "join_datasets": op_join_datasets,
    "concat_datasets": op_concat_datasets,
    "set_compare": op_set_compare,
    "load_tabular": op_load_tabular,
    "reload_artifact": op_reload_artifact,
    "inspect_excel": op_inspect_excel,
    "validate_export": op_validate_export,
    "compare_datasets": op_compare_datasets,
    "get_lineage": op_get_lineage,
    "export_csv": op_export_csv,
    "export_excel": op_export_excel,
    "plot_chart": op_plot_chart,
    "bundle_deliverables": op_bundle_deliverables,
    "match_brief_coverage": op_match_brief_coverage,
    "detect_empty_after_filter": op_detect_empty_after_filter,
    "grain_check": op_grain_check,
}
