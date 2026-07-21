"""Deterministic Agent IV fallback — catalog ops only (no sandbox scripts)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from project_core.domain.analysis.ops import DatasetWorkingSet, execute_op
from project_core.domain.analysis.query_role_classifier import classify_query_roles
from project_core.domain.contracts.analysis_plan import AnalysisPlan, ExecutionCoverage
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.feedback import DataFeedback, ExpectedVsObserved, ProbeRequest

logger = logging.getLogger(__name__)


def analyze_datasets(
    *,
    brief: AnalysisBrief,
    manifest: dict[str, Any],
    profile: dict[str, Any],
    out_dir: str,
    max_steps: int = 8,
    query_meta: list[dict[str, Any]] | None = None,
    analysis_tools: list[dict[str, Any]] | None = None,
    recipe_candidates: list[dict[str, Any]] | None = None,
    analysis_plan: AnalysisPlan | dict[str, Any] | None = None,
    execution_plan: list[dict[str, Any]] | None = None,
    domain_rules_excerpt: str = "",
) -> dict[str, Any]:
    """Run a fixed op-chain fallback and return IV action payload with coverage."""
    del analysis_tools, analysis_plan, execution_plan, domain_rules_excerpt  # unused in op fallback
    paths = [q.get("path") for q in manifest.get("queries", []) if q.get("path")]
    paths, meta = _merge_external_paths(brief, paths, query_meta or [])
    row_counts = {i: int(q.get("row_count", 0)) for i, q in enumerate(manifest.get("queries", []))}

    mode, main_rows, probe_rows, _main_idxs, probe_idxs = classify_query_roles(
        meta, row_counts, num_queries=len(paths)
    )
    product_code = (brief.filters or {}).get("product_code") or (brief.filters or {}).get("sku")

    if mode == "probe_only_success":
        return _probe_success_needs_fact_feedback(brief, probe_idxs, row_counts, paths)

    if mode == "main_empty_probe_hit" and product_code:
        return _identifier_mismatch_feedback(str(product_code), probe_idxs, row_counts, paths)

    if profile.get("row_count", 0) == 0:
        return _empty_feedback(brief, product_code)

    queries = []
    for i, p in enumerate(paths):
        m = meta[i] if i < len(meta) else {}
        queries.append(
            {
                "path": p,
                "ref": f"q{i}",
                "role": m.get("role"),
                "purpose": m.get("purpose"),
                "row_count": row_counts.get(i, 0),
            }
        )

    work_dir = Path(out_dir) / "_ws"
    ws = DatasetWorkingSet.from_manifest({"queries": queries}, meta, work_dir=work_dir)
    steps_run = 0
    gaps: list[str] = []
    new_op_chains: list[dict[str, Any]] = []

    # Prefer recipe tool-chains when present
    chain = _pick_recipe_chain(recipe_candidates or [])
    if not chain:
        chain = _default_op_chain(brief, ws)

    for step in chain:
        if steps_run >= max_steps:
            gaps.append("budget_exceeded")
            break
        op_id = str(step.get("op_id") or "")
        args = dict(step.get("args") or {})
        if step.get("dataset") and "dataset" not in args:
            args["dataset"] = step["dataset"]
        if step.get("save_as"):
            args["save_as"] = step["save_as"]
        res = execute_op(ws, op_id, args, out_dir=out_dir)
        steps_run += 1
        if res.status != "ok":
            gaps.append(f"{op_id}:{res.error or 'error'}")
            continue
        new_op_chains.append({"op_id": op_id, "args": args})

    # Ensure at least one tabular export
    if not ws.artifact_paths and ws.refs():
        ref = ws.refs()[0]
        formats = {str(x).lower() for x in (brief.output_format or [])}
        if "excel" in formats or "xlsx" in formats:
            execute_op(ws, "export_excel", {"dataset": ref, "filename": "analysis.xlsx"}, out_dir=out_dir)
        else:
            execute_op(ws, "export_csv", {"dataset": ref, "filename": f"{ref}.csv"}, out_dir=out_dir)
        steps_run += 1

    if "chart" in {str(x).lower() for x in (brief.output_format or [])} and ws.refs():
        ref = ws.refs()[0]
        cols = list(ws.get(ref).frame().columns)
        if len(cols) >= 2:
            execute_op(
                ws,
                "plot_chart",
                {"dataset": ref, "x": cols[0], "y": cols[1], "kind": "bar", "title": brief.intent[:80]},
                out_dir=out_dir,
            )
            steps_run += 1

    if brief.exploration_mode and main_rows > 0 and steps_run < max_steps:
        clarify = _exploration_clarify(brief, paths, row_counts)
        if clarify:
            return clarify

    arts = list(ws.primary_artifacts or ws.artifact_paths)
    coverage = ExecutionCoverage(
        diagnosis="full" if arts and not gaps else ("partial" if arts else "none"),
        gaps=gaps[:8],
    )
    if _is_impossible_analysis(brief, coverage, steps_run, main_rows, paths):
        return {
            "action": "impossible",
            "reason": "metric_not_mappable",
            "impossible_reason": "brief_metrics_not_found_in_dataset",
            "explanation_vi": "Không thể map metric từ brief sang cột dữ liệu sau khi chạy hết bước phân tích",
        }

    action = "complete" if coverage.diagnosis == "full" else "partial"
    payload: dict[str, Any] = {
        "action": action,
        "headline_metrics": {"row_count": profile.get("row_count", 0)},
        "artifact_paths": arts,
        "chart_artifacts": list(ws.chart_artifacts),
        "excel_artifacts": list(ws.excel_artifacts),
        "caveats": coverage.gaps[:5],
        "sandbox_steps": steps_run,
        "coverage": coverage.model_dump(),
        "new_steps": [],
        "op_chain": new_op_chains,
    }
    return payload


def _pick_recipe_chain(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: list[dict[str, Any]] = []
    best_score = -1.0
    for c in candidates:
        steps = c.get("steps") or c.get("op_chain") or []
        if not steps:
            continue
        # Skip legacy script recipes
        if any(s.get("script_template") or s.get("script") for s in steps if isinstance(s, dict)):
            if not any(s.get("op_id") for s in steps if isinstance(s, dict)):
                continue
        score = float(c.get("score") or 0)
        if score > best_score:
            best_score = score
            best = [s for s in steps if isinstance(s, dict) and s.get("op_id")]
    return best


def _default_op_chain(brief: AnalysisBrief, ws: DatasetWorkingSet) -> list[dict[str, Any]]:
    if not ws.refs():
        return []
    ref = ws.refs()[0]
    df = ws.get(ref).frame()
    cols = [str(c) for c in df.columns]
    chain: list[dict[str, Any]] = [
        {"op_id": "assert_nonempty", "args": {"dataset": ref}},
    ]
    # Heuristic groupby when brief has dimensions + numeric metrics
    dim = None
    for d in brief.dimensions or []:
        for c in cols:
            if d.lower() in c.lower() or c.lower() in d.lower():
                dim = c
                break
        if dim:
            break
    metric_cols = [
        c
        for c in cols
        if pd.api.types.is_numeric_dtype(df[c]) and c != dim
    ]
    if dim and metric_cols:
        aggs = [{"column": metric_cols[0], "fn": "sum", "as": f"{metric_cols[0]}_sum"}]
        chain.append(
            {
                "op_id": "groupby_agg",
                "dataset": ref,
                "save_as": "agg",
                "args": {"by": [dim], "aggs": aggs},
            }
        )
        export_ref = "agg"
    else:
        export_ref = ref

    formats = {str(x).lower() for x in (brief.output_format or [])}
    if "excel" in formats or "xlsx" in formats:
        chain.append({"op_id": "export_excel", "args": {"dataset": export_ref, "filename": "analysis.xlsx"}})
    else:
        chain.append({"op_id": "export_csv", "args": {"dataset": export_ref, "filename": f"{export_ref}.csv"}})
    return chain


def _merge_external_paths(
    brief: AnalysisBrief,
    paths: list[str],
    query_meta: list[dict[str, Any]],
) -> tuple[list[str], list[dict[str, Any]]]:
    meta = list(query_meta)
    while len(meta) < len(paths):
        meta.append({"role": "main"})
    for ext in brief.external_sources or []:
        assets = list(getattr(ext, "datasets", None) or [])
        if assets:
            for asset in assets:
                if asset.path and Path(str(asset.path)).exists():
                    paths.append(str(asset.path))
                    meta.append(
                        {
                            "role": "external",
                            "source": "upload",
                            "source_id": ext.file_id,
                            "sheet_name": asset.sheet_name,
                        }
                    )
            continue
        pp = getattr(ext, "parquet_path", None)
        if pp and Path(str(pp)).exists():
            paths.append(str(pp))
            meta.append({"role": "external", "source": "upload", "source_id": ext.file_id})
    return paths, meta


def _exploration_clarify(
    brief: AnalysisBrief, paths: list[str], row_counts: dict[int, int]
) -> dict[str, Any] | None:
    del brief, paths, row_counts
    return None


def _is_impossible_analysis(
    brief: AnalysisBrief,
    coverage: ExecutionCoverage,
    steps_run: int,
    main_rows: int,
    paths: list[str],
) -> bool:
    if main_rows <= 0 or not paths:
        return False
    if steps_run == 0 and coverage.diagnosis == "none":
        return True
    return False


def _probe_success_needs_fact_feedback(
    brief: AnalysisBrief,
    probe_idxs: list[int],
    row_counts: dict[int, int],
    paths: list[str],
) -> dict[str, Any]:
    del paths
    observed = "; ".join(f"probe_{i}={row_counts.get(i, 0)} rows" for i in probe_idxs)
    return {
        "action": "data_feedback",
        "data_feedback": DataFeedback(
            needs_sql_retry=True,
            issue="probe_success_needs_fact",
            diagnosis="needs_probe",
            summary="Probe đã có dữ liệu master nhưng chưa có fact query phù hợp",
            suggested_intent_fix=brief.intent,
            expected_vs_observed=[
                ExpectedVsObserved(aspect="probe", expected="fact rows", observed=observed)
            ],
            probe_requests=[ProbeRequest(table="STRANS", purpose="fact_after_probe")],
        ).model_dump(),
    }


def _identifier_mismatch_feedback(
    product_code: str,
    probe_idxs: list[int],
    row_counts: dict[int, int],
    paths: list[str],
) -> dict[str, Any]:
    del paths
    observed = "; ".join(f"probe_{i}={row_counts.get(i, 0)} rows" for i in probe_idxs)
    return {
        "action": "data_feedback",
        "data_feedback": DataFeedback(
            needs_sql_retry=True,
            issue="identifier_mismatch",
            diagnosis="solvable",
            summary="Main query empty but product probe returned rows — likely wrong code format",
            suggested_intent_fix=f"retry product lookup for {product_code}",
            expected_vs_observed=[
                ExpectedVsObserved(aspect="product_code", expected=str(product_code), observed=observed)
            ],
            probe_requests=[ProbeRequest(table="SKU_DEF", purpose="sku_lookup")],
        ).model_dump(),
    }


def _empty_feedback(brief: AnalysisBrief, product_code: Any) -> dict[str, Any]:
    return {
        "action": "data_feedback",
        "data_feedback": DataFeedback(
            needs_sql_retry=True,
            issue="empty_result",
            diagnosis="solvable",
            summary="Không có dòng dữ liệu để phân tích theo yêu cầu.",
            suggested_intent_fix=brief.intent,
            expected_vs_observed=[
                ExpectedVsObserved(
                    aspect="row_count",
                    expected=">0",
                    observed="0",
                )
            ],
            probe_requests=(
                [ProbeRequest(table="SKU_DEF", purpose="sku_lookup")] if product_code else []
            ),
        ).model_dump(),
    }
