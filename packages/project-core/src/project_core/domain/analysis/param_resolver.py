from __future__ import annotations

from typing import Any

from project_core.domain.contracts.analysis_plan import AnalysisSubtask
from project_core.domain.contracts.brief import AnalysisBrief


def resolve_params(brief: AnalysisBrief, subtask: AnalysisSubtask | None = None) -> dict[str, Any]:
    """Derive recipe params from brief/subtask for script substitution."""
    filters = dict(brief.filters or {})
    if subtask:
        filters = {**filters, **(subtask.filters or {})}

    params: dict[str, Any] = {}

    if filters.get("card_prefix"):
        params["card_prefix"] = str(filters["card_prefix"])
    if filters.get("loyalty_tier"):
        params["loyalty_tier"] = str(filters["loyalty_tier"])
    if filters.get("product_code") or filters.get("sku"):
        params["product_code"] = str(filters.get("product_code") or filters.get("sku"))
    if filters.get("lookup_mode"):
        params["lookup_mode"] = str(filters["lookup_mode"])

    dims = list(subtask.dimensions if subtask and subtask.dimensions else brief.dimensions) or []
    if dims:
        params["group_by"] = dims[0]
    elif "store" in (subtask.intent if subtask else brief.intent).lower():
        params["group_by"] = "STK_ID"
    elif any(k in (subtask.intent if subtask else brief.intent).lower() for k in ("tháng", "month", "trend")):
        params["group_by"] = "month"

    tr = brief.time_range
    if tr.start:
        params["time_start"] = tr.start
    if tr.end:
        params["time_end"] = tr.end
    if tr.grain:
        params["time_grain"] = tr.grain

    if "chart" in (brief.output_format or []):
        params["make_chart"] = True

    metrics = list(subtask.metrics if subtask else brief.metrics) or []
    if metrics:
        params["metric"] = metrics[0]

    return params


def apply_param_schema_defaults(
    param_schema: list[dict[str, Any]],
    resolved: dict[str, Any],
) -> dict[str, Any]:
    out = dict(resolved)
    for spec in param_schema:
        name = spec.get("name")
        if not name or name in out:
            continue
        if "default" in spec and spec["default"] is not None:
            out[name] = spec["default"]
        elif spec.get("enum"):
            out[name] = spec["enum"][0]
    return out
