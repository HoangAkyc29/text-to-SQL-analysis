"""dataframe-ops MCP — catalog ops on disk-backed working set."""

from __future__ import annotations

from typing import Any

from project_core.domain.analysis import disk_ws
from project_core.domain.analysis.ops import execute_op
from project_core.domain.analysis.ops.registry import list_op_ids
from project_core.domain.analysis.ops.working_set import DatasetWorkingSet

# Ops that belong on dataframe-ops (not deliverables).
_DELIVERABLE_OPS = {
    "export_csv",
    "export_excel",
    "plot_chart",
    "bundle_deliverables",
    "inspect_excel",
    "validate_export",
}


def _ws() -> DatasetWorkingSet:
    root = disk_ws.work_dir()
    ws = DatasetWorkingSet(work_dir=root / "_handles")
    ws.set_output_root(str(disk_ws.out_dir()))
    for prof in disk_ws.list_dataset_profiles(root=root):
        ref = str(prof.get("ref") or "")
        if not ref or ws.has(ref):
            continue
        try:
            df = disk_ws.read_frame(ref, root=root)
            ws.save_frame(ref, df, role="hydrate", source="disk_ws")
        except Exception:  # noqa: BLE001
            continue
    return ws


def _persist(ws: DatasetWorkingSet, result: Any) -> None:
    for ref in ws.refs():
        try:
            disk_ws.write_frame(ref, ws.get(ref).frame())
        except Exception:  # noqa: BLE001
            continue


def _call(op_id: str, args: dict[str, Any]) -> dict[str, Any]:
    if op_id not in set(list_op_ids()) or op_id in _DELIVERABLE_OPS:
        return {"ok": False, "error": f"op_not_on_dataframe_ops:{op_id}"}
    ws = _ws()
    out = execute_op(ws, op_id, args, out_dir=str(disk_ws.out_dir()))
    _persist(ws, out)
    obs = out.as_observation()
    return {"ok": out.status == "ok", **obs}


def list_datasets() -> dict[str, Any]:
    """List working-set datasets with columns and row counts."""
    return _call("list_datasets", {})


def head_rows(dataset: str, n: int = 5) -> dict[str, Any]:
    """First n rows of a dataset."""
    return _call("head_rows", {"dataset": dataset, "n": n})


def describe_columns(dataset: str) -> dict[str, Any]:
    """Column stats for a dataset."""
    return _call("describe_columns", {"dataset": dataset})


def value_counts(dataset: str, column: str, n: int = 20) -> dict[str, Any]:
    """Top-k value counts for a column."""
    return _call("value_counts", {"dataset": dataset, "column": column, "n": n})


def cast_column(
    dataset: str,
    column: str,
    to: str = "str",
    save_as: str | None = None,
) -> dict[str, Any]:
    """Cast a column dtype."""
    args: dict[str, Any] = {"dataset": dataset, "column": column, "to": to}
    if save_as:
        args["save_as"] = save_as
    return _call("cast_column", args)


def tcvn3_converter(
    dataset: str,
    columns: list[str] | str | None = None,
    save_as: str | None = None,
) -> dict[str, Any]:
    """Decode TCVN3/legacy Vietnamese text columns to Unicode (alias TCVN3_converter)."""
    args: dict[str, Any] = {"dataset": dataset}
    if columns is not None:
        args["columns"] = columns
    if save_as:
        args["save_as"] = save_as
    return _call("tcvn3_converter", args)


# Public alias matching the product name used in skills / prompts.
TCVN3_converter = tcvn3_converter


def filter_rows(
    dataset: str,
    column: str | None = None,
    op: str | None = None,
    value: Any = None,
    clauses: list[dict[str, Any]] | None = None,
    save_as: str | None = None,
) -> dict[str, Any]:
    """Filter rows by column op or clauses AND/OR."""
    args: dict[str, Any] = {"dataset": dataset}
    if clauses:
        args["clauses"] = clauses
    if column is not None:
        args["column"] = column
        args["op"] = op or "eq"
        args["value"] = value
    if save_as:
        args["save_as"] = save_as
    return _call("filter_rows", args)


def select_columns(dataset: str, columns: list[str], save_as: str | None = None) -> dict[str, Any]:
    """Project columns into a new dataset."""
    args: dict[str, Any] = {"dataset": dataset, "columns": columns}
    if save_as:
        args["save_as"] = save_as
    return _call("select_columns", args)


def sort_rows(dataset: str, by: list[str] | str, ascending: bool = True, save_as: str | None = None) -> dict[str, Any]:
    """Sort rows by columns."""
    args: dict[str, Any] = {"dataset": dataset, "by": by, "ascending": ascending}
    if save_as:
        args["save_as"] = save_as
    return _call("sort_rows", args)


def limit_rows(dataset: str, n: int = 100, offset: int = 0, save_as: str | None = None) -> dict[str, Any]:
    """Slice first n rows."""
    args: dict[str, Any] = {"dataset": dataset, "n": n, "offset": offset}
    if save_as:
        args["save_as"] = save_as
    return _call("limit_rows", args)


def groupby_agg(
    dataset: str,
    by: list[str] | str,
    aggs: Any,
    save_as: str | None = None,
) -> dict[str, Any]:
    """Group-by aggregations."""
    args: dict[str, Any] = {"dataset": dataset, "by": by, "aggs": aggs}
    if save_as:
        args["save_as"] = save_as
    return _call("groupby_agg", args)


def join_datasets(
    left: str,
    right: str,
    how: str = "inner",
    on: str | list[str] | None = None,
    left_on: str | list[str] | None = None,
    right_on: str | list[str] | None = None,
    save_as: str | None = None,
) -> dict[str, Any]:
    """Join two datasets."""
    args: dict[str, Any] = {"left": left, "right": right, "how": how}
    if on is not None:
        args["on"] = on
    if left_on is not None:
        args["left_on"] = left_on
    if right_on is not None:
        args["right_on"] = right_on
    if save_as:
        args["save_as"] = save_as
    return _call("join_datasets", args)


def top_n_per_group(
    dataset: str,
    partition_by: list[str] | str,
    order_by: list[str] | str,
    n: int = 5,
    ascending: bool = False,
    save_as: str | None = None,
) -> dict[str, Any]:
    """Keep top n rows per group."""
    args: dict[str, Any] = {
        "dataset": dataset,
        "partition_by": partition_by,
        "order_by": order_by,
        "n": n,
        "ascending": ascending,
    }
    if save_as:
        args["save_as"] = save_as
    return _call("top_n_per_group", args)
