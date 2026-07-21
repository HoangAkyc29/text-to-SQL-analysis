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
    "top_n_per_group": "Keep top n rows per group",
    "percent_of_total": "Add percent-of-total column",
    "cumulative_sum": "Add cumulative sum column",
    "join_datasets": "Join two datasets",
    "concat_datasets": "Concatenate datasets",
    "set_compare": "left_only / right_only / both on keys",
    "export_csv": "Write CSV under out/",
    "export_excel": "Write Excel (optional multi-sheet map)",
    "plot_chart": "Write PNG chart bar|line|pie|hist",
    "bundle_deliverables": "Mark primary artifacts for sufficiency",
    "match_brief_coverage": "Compare brief metrics/dims vs available columns",
    "detect_empty_after_filter": "Flag empty dataset for feedback",
    "grain_check": "Check one-row-per-key vs many grain",
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


def execute_op(
    ws: DatasetWorkingSet,
    op_id: str,
    args: dict[str, Any] | None,
    *,
    out_dir: str | Path,
) -> OpResult:
    """Validate op_id and run handler. Never executes free-form scripts."""
    args = dict(args or {})
    if op_id not in HANDLERS:
        return OpResult(op_id=op_id, status="error", error=f"unknown_op:{op_id}")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    # Inject save_as from top-level if provided alongside args
    try:
        raw = HANDLERS[op_id](ws, args, out)
    except KeyError as exc:
        return OpResult(op_id=op_id, status="error", error=str(exc))
    except Exception as exc:  # noqa: BLE001
        return OpResult(op_id=op_id, status="error", error=f"op_failed:{exc}")
    if isinstance(raw, dict) and raw.get("error"):
        return OpResult(op_id=op_id, status="error", result=raw, error=str(raw["error"]))
    return OpResult(op_id=op_id, status="ok", result=raw if isinstance(raw, dict) else {"value": raw})


def catalog_for_prompt() -> list[dict[str, str]]:
    return [{"op_id": k, "description": v} for k, v in sorted(OP_CATALOG.items())]
