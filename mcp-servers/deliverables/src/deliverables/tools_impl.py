"""deliverables MCP — export / plot / inspect."""

from __future__ import annotations

from typing import Any

from project_core.domain.analysis import disk_ws
from project_core.domain.analysis.ops import execute_op
from project_core.domain.analysis.ops.working_set import DatasetWorkingSet


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


def _call(op_id: str, args: dict[str, Any]) -> dict[str, Any]:
    ws = _ws()
    out = execute_op(ws, op_id, args, out_dir=str(disk_ws.out_dir()))
    obs = out.as_observation()
    return {
        "ok": out.status == "ok",
        "artifact_paths": list(ws.artifact_paths),
        **obs,
    }


def export_excel(
    dataset: str | None = None,
    filename: str = "analysis_result.xlsx",
    sheets: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Write Excel under out/ (dataset or multi-sheet map)."""
    args: dict[str, Any] = {"filename": filename}
    if sheets:
        args["sheets"] = sheets
    elif dataset:
        args["dataset"] = dataset
    return _call("export_excel", args)


def export_csv(dataset: str, filename: str = "analysis_result.csv") -> dict[str, Any]:
    """Write CSV under out/."""
    return _call("export_csv", {"dataset": dataset, "filename": filename})


def plot_chart(
    dataset: str,
    x: str,
    y: str,
    chart_type: str = "bar",
    filename: str | None = None,
) -> dict[str, Any]:
    """Write PNG chart (bar|line|pie|hist)."""
    args: dict[str, Any] = {"dataset": dataset, "x": x, "y": y, "chart_type": chart_type}
    if filename:
        args["filename"] = filename
    return _call("plot_chart", args)


def bundle_deliverables(artifact_ids: list[str] | None = None) -> dict[str, Any]:
    """Mark primary artifacts for sufficiency."""
    return _call("bundle_deliverables", {"artifact_ids": artifact_ids or []})


def inspect_excel(source_ref: str | None = None, artifact_id: str | None = None) -> dict[str, Any]:
    """Inspect workbook sheets, headers, shapes and samples."""
    args: dict[str, Any] = {}
    if source_ref:
        args["source_ref"] = source_ref
    if artifact_id:
        args["artifact_id"] = artifact_id
    return _call("inspect_excel", args)


def validate_export(artifact_id: str) -> dict[str, Any]:
    """Reopen and validate a registered export against its source."""
    return _call("validate_export", {"artifact_id": artifact_id})
