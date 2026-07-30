"""Op registry and execute_op entrypoint."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from project_core.domain.analysis.ops.handlers import HANDLERS
from project_core.domain.analysis.ops.working_set import DatasetWorkingSet

# Short catalog descriptions for LLM prompts / TOOLS.md generation.
OP_CATALOG: dict[str, str] = {
    "list_datasets": "List working-set datasets with columns, dtypes, row_count, sample",
    "describe_columns": "Column stats: null%, nunique, min/max or top values",
    "head_rows": "First n rows of a dataset",
    "sample_rows": "Random sample of n rows",
    "value_counts": "Top-k value counts for a column",
    "null_report": "Null counts/fractions per column",
    "assert_nonempty": "Check dataset has rows (ok flag for critic)",
    "assert_columns_present": "Check required columns exist",
    "select_columns": "Project columns; save_as new dataset",
    "rename_columns": "Rename via mapping; save_as",
    "drop_columns": "Drop columns; save_as",
    "cast_column": "Cast column to int|float|str|datetime",
    "tcvn3_converter": (
        "Decode TCVN3/legacy Vietnamese text columns to Unicode "
        "(alias TCVN3_converter). Pass columns= or omit for all string cols. "
        "Columns ending in _U are already Unicode and are never converted."
    ),
    "add_column_expr": "Add column from safe DSL expr",
    "fill_null": "Fill nulls with value",
    "drop_null": "Drop rows with nulls",
    "filter_rows": "Filter by column op (eq,gte,contains,...) or clauses AND/OR",
    "sort_rows": "Sort by columns",
    "limit_rows": "Slice first n rows (optional offset)",
    "distinct_rows": "Distinct rows (optional subset columns)",
    "drop_duplicates": "Alias of distinct_rows",
    "groupby_agg": "Group-by aggregations sum|mean|count|...",
    "pivot_table": "Pivot table",
    "melt": "Unpivot / melt",
    "window_rank": "Rank within partition",
    "top_n_per_group": (
        "Keep top n rows per partition (group_by/partition_by). "
        "For 'top N per product/SKU', set group_by=SKU_ID and order_by date/time "
        "(not a global limit_rows). Empty partition_by = global top-N."
    ),
    "percent_of_total": "Add percent-of-total column",
    "cumulative_sum": "Add cumulative sum column",
    "join_datasets": "Join two datasets",
    "concat_datasets": "Concatenate datasets",
    "set_compare": "left_only / right_only / both on keys",
    "load_tabular": "Load an allowlisted parquet/CSV/XLSX source into the working set",
    "reload_artifact": "Reload a registered CSV/XLSX artifact as a dataset",
    "inspect_excel": "Inspect workbook sheets, headers, shapes and samples",
    "validate_export": "Reopen and validate a registered export against its source",
    "compare_datasets": "Compare datasets by keys or row-hash multiset",
    "get_lineage": "Return dataset/artifact lineage",
    "export_csv": "Write CSV under out/",
    "export_excel": (
        "Write Excel under out/. Prefer sheets={bills:<top_n_per_group_ref>, summary:<agg_ref>} "
        "when the brief asks for top-N bills per product plus quantity. "
        "Never replace a per-group top-N bills frame with a global 5-row slice."
    ),
    "plot_chart": "Write PNG chart bar|line|pie|hist",
    "bundle_deliverables": "Mark primary artifacts for sufficiency",
    "match_brief_coverage": "Compare brief metrics/dims vs available columns",
    "detect_empty_after_filter": "Flag empty dataset for feedback",
    "grain_check": "Check one-row-per-key vs many grain",
}

REQUIRED_ARGS: dict[str, tuple[str, ...]] = {
    "describe_columns": ("dataset",),
    "head_rows": ("dataset",),
    "sample_rows": ("dataset",),
    "value_counts": ("dataset", "column"),
    "null_report": ("dataset",),
    "assert_nonempty": ("dataset",),
    "assert_columns_present": ("dataset", "columns"),
    "select_columns": ("dataset", "columns"),
    "rename_columns": ("dataset", "mapping"),
    "drop_columns": ("dataset", "columns"),
    "cast_column": ("dataset", "column"),
    "tcvn3_converter": ("dataset",),
    "add_column_expr": ("dataset", "name", "expr"),
    "fill_null": ("dataset",),
    "drop_null": ("dataset",),
    "filter_rows": ("dataset",),
    "sort_rows": ("dataset", "by"),
    "limit_rows": ("dataset",),
    "distinct_rows": ("dataset",),
    "drop_duplicates": ("dataset",),
    "groupby_agg": ("dataset", "by", "aggs"),
    "pivot_table": ("dataset",),
    "melt": ("dataset",),
    "window_rank": ("dataset", "order_by"),
    "top_n_per_group": ("dataset", "partition_by", "order_by"),
    "percent_of_total": ("dataset", "column"),
    "cumulative_sum": ("dataset", "column"),
    "join_datasets": ("left", "right"),
    "concat_datasets": ("datasets",),
    "set_compare": ("left", "right"),
    "export_csv": ("dataset",),
    "export_excel": (),
    "plot_chart": ("dataset", "x", "y"),
    "load_tabular": ("source_ref",),
    "reload_artifact": ("artifact_id",),
    "inspect_excel": (),
    "validate_export": ("artifact_id",),
    "compare_datasets": ("left", "right"),
    "get_lineage": (),
}

ARG_ALIASES: dict[str, dict[str, tuple[str, ...]]] = {
    "cast_column": {
        "column": ("column_name", "columns"),
        "to": ("dtype", "target_type", "type"),
    },
    "tcvn3_converter": {
        "columns": ("column", "column_name", "cols", "fields"),
        "dataset": ("data", "source", "frame", "table", "ref"),
    },
    "groupby_agg": {
        "by": ("group_by", "groupby"),
        "aggs": ("aggregations", "aggregate"),
    },
    "sort_rows": {"by": ("columns", "sort_by")},
    "top_n_per_group": {
        "partition_by": ("group_by", "partition", "by"),
        "order_by": ("sort_by", "order", "column"),
    },
    "window_rank": {
        "partition_by": ("group_by", "partition"),
        "order_by": ("sort_by", "order", "column"),
    },
    "plot_chart": {"x": ("x_column",), "y": ("y_column", "value_column")},
    "export_excel": {
        "dataset": ("data", "source", "frame", "table", "ref"),
        "filename": ("path", "file", "file_name", "name", "output"),
        "sheets": ("sheet_map", "workbook"),
    },
    "export_csv": {
        "dataset": ("data", "source", "frame", "table", "ref"),
        "filename": ("path", "file", "file_name", "name", "output"),
    },
    "join_datasets": {
        "left": ("left_dataset", "left_dataset_name", "left_ref", "left_df", "lhs"),
        "right": ("right_dataset", "right_dataset_name", "right_ref", "right_df", "rhs"),
        "on": ("join_on", "keys", "key"),
        "left_on": ("left_key", "left_keys"),
        "right_on": ("right_key", "right_keys"),
    },
    "filter_rows": {
        "clauses": ("conditions", "filters", "predicates"),
        "column": ("column_name", "col", "field"),
        "op": ("operator", "cmp", "predicate"),
        "dataset": ("data", "source", "frame", "table", "ref", "input_df"),
    },
    "select_columns": {
        "dataset": ("data", "source", "frame", "table", "ref", "input_df"),
        "columns": ("cols", "fields", "column_list"),
    },
}

MUTATING_OPS = {
    "select_columns", "rename_columns", "drop_columns", "cast_column",
    "tcvn3_converter",
    "add_column_expr", "fill_null", "drop_null", "filter_rows", "sort_rows",
    "limit_rows", "distinct_rows", "drop_duplicates", "groupby_agg",
    "pivot_table", "melt", "window_rank", "top_n_per_group",
    "percent_of_total", "cumulative_sum", "join_datasets", "concat_datasets",
    "set_compare", "load_tabular", "reload_artifact",
}

# Planner / skill aliases → canonical op_id.
OP_ID_ALIASES: dict[str, str] = {
    "TCVN3_converter": "tcvn3_converter",
    "tcvn3_convert": "tcvn3_converter",
}


@dataclass(frozen=True)
class OpSpec:
    op_id: str
    description: str
    required_args: tuple[str, ...] = ()
    mutates_working_set: bool = False
    output_kind: str = "observation"
    arg_aliases: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def for_prompt(self) -> dict[str, Any]:
        return {
            "op_id": self.op_id,
            "description": self.description,
            "args_schema": {
                "type": "object",
                "required": list(self.required_args),
                "additionalProperties": True,
            },
            "mutates_working_set": self.mutates_working_set,
            "output_kind": self.output_kind,
            "accepted_arg_aliases": {
                key: list(value) for key, value in self.arg_aliases.items()
            },
        }


OP_SPECS: dict[str, OpSpec] = {
    op_id: OpSpec(
        op_id=op_id,
        description=description,
        required_args=REQUIRED_ARGS.get(op_id, ()),
        mutates_working_set=op_id in MUTATING_OPS,
        output_kind="artifact" if op_id.startswith("export_") or op_id == "plot_chart" else "observation",
        arg_aliases=ARG_ALIASES.get(op_id, {}),
    )
    for op_id, description in OP_CATALOG.items()
}


@dataclass
class OpResult:
    op_id: str
    status: str  # ok | error
    result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def as_observation(self) -> dict[str, Any]:
        obs = {"op_id": self.op_id, "status": self.status, **self.result}
        if self.error:
            obs["error"] = self.error
        return obs


def list_op_ids() -> list[str]:
    return sorted(HANDLERS.keys())


def normalize_op_args(op_id: str, args: dict[str, Any] | None) -> tuple[dict[str, Any], list[str]]:
    """Canonicalize common planner aliases before schema validation."""
    normalized = dict(args or {})
    repairs: list[str] = []
    for canonical, aliases in ARG_ALIASES.get(op_id, {}).items():
        if normalized.get(canonical) is not None:
            continue
        for alias in aliases:
            if normalized.get(alias) is None:
                continue
            value = normalized[alias]
            if canonical == "column" and isinstance(value, list) and len(value) == 1:
                value = value[0]
            normalized[canonical] = value
            repairs.append(f"{alias}->{canonical}")
            break
    return normalized, repairs


def missing_required_args(op_id: str, args: dict[str, Any] | None) -> list[str]:
    normalized, _ = normalize_op_args(op_id, args)
    spec = OP_SPECS.get(op_id)
    missing = [
        name
        for name in (spec.required_args if spec else ())
        if normalized.get(name) is None
    ]
    if op_id == "export_excel" and not normalized.get("dataset") and not normalized.get("sheets"):
        missing.append("dataset_or_sheets")
    if (
        op_id == "inspect_excel"
        and not normalized.get("source_ref")
        and not normalized.get("artifact_id")
    ):
        missing.append("source_ref_or_artifact_id")
    return missing


def execute_op(
    ws: DatasetWorkingSet,
    op_id: str,
    args: dict[str, Any] | None,
    *,
    out_dir: str | Path,
) -> OpResult:
    """Validate op_id and run handler. Never executes free-form scripts."""
    op_id = OP_ID_ALIASES.get(op_id, op_id)
    args, repairs = normalize_op_args(op_id, args)
    if op_id not in HANDLERS:
        return OpResult(op_id=op_id, status="error", error=f"unknown_op:{op_id}")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ws.set_output_root(out)
    missing = missing_required_args(op_id, args)
    if missing:
        spec = OP_SPECS.get(op_id)
        return OpResult(
            op_id=op_id,
            status="error",
            result={
                "required_args": list(spec.required_args if spec else ()),
                "received_args": sorted(args),
                "accepted_arg_aliases": {
                    key: list(value)
                    for key, value in ARG_ALIASES.get(op_id, {}).items()
                },
            },
            error=f"missing_args:{missing}",
        )
    # Inject save_as from top-level if provided alongside args
    try:
        raw = HANDLERS[op_id](ws, args, out)
    except KeyError as exc:
        return OpResult(op_id=op_id, status="error", error=str(exc))
    except Exception as exc:  # noqa: BLE001
        return OpResult(op_id=op_id, status="error", error=f"op_failed:{exc}")
    if isinstance(raw, dict) and raw.get("error"):
        return OpResult(op_id=op_id, status="error", result=raw, error=str(raw["error"]))
    result = raw if isinstance(raw, dict) else {"value": raw}
    if repairs:
        result = {**result, "arg_repairs": repairs}
    return OpResult(op_id=op_id, status="ok", result=result)


def catalog_for_prompt() -> list[dict[str, Any]]:
    return [OP_SPECS[k].for_prompt() for k in sorted(OP_SPECS)]
