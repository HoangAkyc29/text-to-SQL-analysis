"""Filter / sort / slice / shape / inspect / export / agg / join / critic ops."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import pandas as pd

from project_core.domain.analysis.ops.expr_dsl import eval_column_expr
from project_core.domain.analysis.ops.working_set import DatasetWorkingSet

OpHandler = Callable[[DatasetWorkingSet, dict[str, Any], Path], dict[str, Any]]


def _require_cols(df: pd.DataFrame, cols: list[str]) -> str | None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        return f"missing_columns:{missing}"
    return None


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
    handle = ws.save_frame(save_as, df, role=role, source=source)
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
    col = str(args["column"])
    to = str(args.get("to") or "str").lower()
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


def _clause_mask(df: pd.DataFrame, clause: dict[str, Any]) -> pd.Series:
    col = str(clause["column"])
    op = str(clause.get("op") or "eq").lower()
    value = clause.get("value")
    case_insensitive = bool(clause.get("case_insensitive", False))
    if col not in df.columns:
        raise KeyError(f"missing_columns:[{col}]")
    s = df[col]
    if op == "is_null":
        return s.isna()
    if op == "not_null":
        return s.notna()
    if op in {"contains", "not_contains", "startswith", "endswith", "regex", "eq", "ne"} and case_insensitive:
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
    clauses = args.get("clauses")
    try:
        if clauses:
            how = str(args.get("combine") or "and").lower()
            masks = [_clause_mask(df, c) for c in clauses]
            mask = _combine_masks(masks, how)
        else:
            # Single-clause shorthand
            mask = _clause_mask(
                df,
                {
                    "column": args["column"],
                    "op": args.get("op", "eq"),
                    "value": args.get("value"),
                    "case_insensitive": args.get("case_insensitive", False),
                },
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


def op_groupby_agg(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    by = [str(c) for c in (args.get("by") or [])]
    aggs = args.get("aggs") or []
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
    grouped = handle.frame().groupby(by, dropna=False).agg(**{k: v for k, v in named.items()})
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
    partition_by = [str(c) for c in (args.get("partition_by") or [])]
    order_by = [str(c) for c in (args.get("order_by") or [])]
    ascending = args.get("ascending", False)
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
    partition_by = [str(c) for c in (args.get("partition_by") or args.get("group_by") or [])]
    order_by = [str(c) for c in (args.get("order_by") or [])]
    n = int(args.get("n") or 5)
    ascending = args.get("ascending", False)
    err = _require_cols(handle.frame(), partition_by + order_by)
    if err:
        return {"error": err}
    if isinstance(ascending, list):
        asc = [bool(x) for x in ascending]
    else:
        asc = [bool(ascending)] * len(order_by)
    df = handle.frame().sort_values(by=partition_by + order_by, ascending=[True] * len(partition_by) + asc)
    df = df.copy()
    df["_rn"] = df.groupby(partition_by, dropna=False).cumcount() + 1
    out = df.loc[df["_rn"] <= n].drop(columns=["_rn"])
    return _save(ws, args.get("save_as"), out, source="top_n_per_group", role=handle.role)


def op_percent_of_total(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    col = str(args["column"])
    out_col = str(args.get("as") or f"{col}_pct")
    group_by = [str(c) for c in (args.get("group_by") or [])]
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
    group_by = [str(c) for c in (args.get("group_by") or [])]
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
    try:
        if on:
            merged = left.merge(right, how=how, on=on, suffixes=args.get("suffixes") or ("_x", "_y"))
        else:
            merged = left.merge(
                right,
                how=how,
                left_on=left_on,
                right_on=right_on,
                suffixes=args.get("suffixes") or ("_x", "_y"),
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


# ----- F. Export -----


def op_export_csv(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    handle = ws.get(str(args["dataset"]))
    name = str(args.get("filename") or f"{handle.ref}.csv")
    if not name.endswith(".csv"):
        name += ".csv"
    path = out_dir / name
    handle.frame().to_csv(path, index=False)
    primary = bool(args.get("primary", True))
    ws.register_artifact(str(path), kind="file", primary=primary)
    return {"path": str(path), "row_count": int(len(handle.frame())), "artifact": True}


def op_export_excel(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    sheets = args.get("sheets")  # {sheet_name: dataset_ref}
    name = str(args.get("filename") or "analysis.xlsx")
    if not name.endswith(".xlsx"):
        name += ".xlsx"
    path = out_dir / name
    try:
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            if sheets:
                for sheet, ref in sheets.items():
                    ws.get(str(ref)).frame().to_excel(writer, sheet_name=str(sheet)[:31], index=False)
            else:
                ref = str(args["dataset"])
                ws.get(ref).frame().to_excel(writer, sheet_name="data", index=False)
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}
    ws.register_artifact(str(path), kind="excel", primary=bool(args.get("primary", True)))
    return {"path": str(path), "artifact": True, "kind": "excel"}


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
    err = _require_cols(df, [x, y])
    if err:
        return {"error": err}
    name = str(args.get("filename") or f"{handle.ref}_{kind}.png")
    if not name.endswith(".png"):
        name += ".png"
    path = out_dir / name
    plt.figure(figsize=(10, 6))
    try:
        if kind == "bar":
            plt.bar(df[x].astype(str), pd.to_numeric(df[y], errors="coerce"))
        elif kind == "line":
            plt.plot(df[x].astype(str), pd.to_numeric(df[y], errors="coerce"))
        elif kind == "pie":
            plt.pie(pd.to_numeric(df[y], errors="coerce").fillna(0), labels=df[x].astype(str), autopct="%1.1f%%")
        elif kind == "hist":
            plt.hist(pd.to_numeric(df[y], errors="coerce").dropna())
        else:
            plt.bar(df[x].astype(str), pd.to_numeric(df[y], errors="coerce"))
        if title:
            plt.title(title)
        plt.tight_layout()
        plt.savefig(path)
    finally:
        plt.close()
    ws.register_artifact(str(path), kind="chart", primary=bool(args.get("primary", True)))
    return {"path": str(path), "artifact": True, "kind": "chart"}


def op_bundle_deliverables(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    paths = [str(p) for p in (args.get("paths") or [])]
    for p in paths:
        kind = "excel" if p.endswith(".xlsx") else ("chart" if p.endswith(".png") else "file")
        ws.register_artifact(p, kind=kind, primary=True)
    if not paths:
        # Mark all current artifacts as primary
        for p in list(ws.artifact_paths):
            ws.register_artifact(p, primary=True)
    return {"primary_artifacts": list(ws.primary_artifacts), "artifact_paths": list(ws.artifact_paths)}


# ----- G. Critic -----


def op_match_brief_coverage(ws: DatasetWorkingSet, args: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    brief = args.get("brief") or {}
    metrics = [str(m).lower() for m in (brief.get("metrics") or [])]
    dimensions = [str(d).lower() for d in (brief.get("dimensions") or [])]
    all_cols: set[str] = set()
    total_rows = 0
    for prof in ws.list_profiles():
        if prof.get("error"):
            continue
        all_cols.update(str(c).lower() for c in (prof.get("columns") or []))
        total_rows += int(prof.get("row_count") or 0)

    def _present(names: list[str]) -> tuple[list[str], list[str]]:
        found, missing = [], []
        for n in names:
            if any(n in c or c in n for c in all_cols):
                found.append(n)
            else:
                missing.append(n)
        return found, missing

    m_found, m_missing = _present(metrics)
    d_found, d_missing = _present(dimensions)
    ok = total_rows > 0 and not m_missing
    return {
        "ok": ok,
        "total_rows": total_rows,
        "columns": sorted(all_cols),
        "metrics_found": m_found,
        "metrics_missing": m_missing,
        "dimensions_found": d_found,
        "dimensions_missing": d_missing,
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
    "export_csv": op_export_csv,
    "export_excel": op_export_excel,
    "plot_chart": op_plot_chart,
    "bundle_deliverables": op_bundle_deliverables,
    "match_brief_coverage": op_match_brief_coverage,
    "detect_empty_after_filter": op_detect_empty_after_filter,
    "grain_check": op_grain_check,
}
