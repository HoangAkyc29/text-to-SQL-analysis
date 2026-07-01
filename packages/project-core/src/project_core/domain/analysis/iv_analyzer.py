from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from project_core.domain.analysis.execution_composer import build_execution_plan
from project_core.domain.analysis.recipe_matcher import rank_candidates
from project_core.domain.contracts.analysis_plan import (
    AnalysisPlan,
    ExecutionCoverage,
    ExecutionStepPlan,
    RecipeCandidate,
    RecipeStep,
)
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import ClarificationRequest
from project_core.domain.contracts.feedback import DataFeedback, ExpectedVsObserved, ProbeRequest
from project_core.domain.feedback.analysis_tool_registry import apply_params_to_script


def _sandbox():
    from python_sandbox import tools_impl

    return tools_impl


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
    """Run composable sandbox steps and return IV action payload with coverage."""
    paths = [q.get("path") for q in manifest.get("queries", []) if q.get("path")]
    paths, meta = _merge_external_paths(brief, paths, query_meta or [])
    row_counts = {i: int(q.get("row_count", 0)) for i, q in enumerate(manifest.get("queries", []))}

    probe_idxs = [i for i, m in enumerate(meta) if m.get("role") == "probe"]
    main_idxs = [i for i, m in enumerate(meta) if m.get("role") != "probe"]
    if not main_idxs:
        main_idxs = list(range(len(paths)))

    main_rows = sum(row_counts.get(i, 0) for i in main_idxs)
    probe_rows = sum(row_counts.get(i, 0) for i in probe_idxs)
    product_code = (brief.filters or {}).get("product_code") or (brief.filters or {}).get("sku")

    if main_rows == 0 and probe_rows > 0 and product_code:
        return _identifier_mismatch_feedback(str(product_code), probe_idxs, row_counts, paths)

    if profile.get("row_count", 0) == 0:
        return _empty_feedback(brief, product_code)

    plan = _coerce_plan(analysis_plan, brief)

    sandbox = _sandbox()
    external_paths = [p for i, p in enumerate(paths) if i < len(meta) and meta[i].get("role") == "external"]
    sql_paths = [p for i, p in enumerate(paths) if i < len(meta) and meta[i].get("role") != "external"]
    if external_paths and sql_paths and Path(sql_paths[0]).exists() and Path(external_paths[0]).exists():
        merged_out = str(Path(out_dir) / "merged_upload.parquet")
        try:
            merge_result = sandbox.merge_datasets(sql_paths[0], external_paths[0], merged_out)
            if merge_result.get("status") == "ok":
                paths = [merged_out] + paths
                meta = [{"role": "merged", "join_key": merge_result.get("join_key")}] + meta
        except Exception:
            pass

    exec_steps, coverage = _resolve_execution(
        plan=plan,
        paths=paths,
        meta=meta,
        brief=brief,
        analysis_tools=analysis_tools or [],
        recipe_candidates=recipe_candidates or [],
        execution_plan=execution_plan,
    )

    steps_run = 0
    artifacts: list[str] = []
    metrics: dict[str, Any] = {"row_count": profile.get("row_count", 0)}
    new_steps: list[RecipeStep] = []

    for path in paths[:2]:
        if steps_run >= max_steps:
            break
        if path and Path(path).exists():
            preview = sandbox.preview_dataframe(path, n=30)
            steps_run += 1
            if "error" not in preview:
                metrics[f"preview_rows_{steps_run}"] = len(preview.get("preview", []))

    for exec_step in exec_steps:
        if steps_run >= max_steps:
            coverage.gaps.append(f"budget_exceeded:{exec_step.subtask_id}")
            break
        step = exec_step.step
        dpath = exec_step.dataset_path or (paths[0] if paths else "")
        if not dpath or not Path(dpath).exists():
            coverage.gaps.append(f"missing_dataset:{exec_step.subtask_id}")
            continue
        sub_out = str(Path(out_dir) / exec_step.subtask_id)
        Path(sub_out).mkdir(parents=True, exist_ok=True)
        script = apply_params_to_script(step.script_template, step.params)
        try:
            result = sandbox.run_analysis_script(dpath, script, sub_out)
            steps_run += 1
            if result.get("status") == "ok":
                artifacts.extend(result.get("artifacts") or [])
            if step.status == "generated":
                new_steps.append(step)
        except Exception:
            coverage.gaps.append(f"step_failed:{step.step_id}")

    if "chart" in (brief.output_format or []) and paths and steps_run < max_steps:
        primary = paths[0]
        if primary and Path(primary).exists():
            cols = _column_names(primary)
            if len(cols) >= 2:
                chart_path = str(Path(out_dir) / "chart.png")
                try:
                    sandbox.plot_chart(primary, chart_path, cols[0], cols[1], title=brief.intent[:80])
                    artifacts.append(chart_path)
                    steps_run += 1
                except Exception:
                    pass

    if brief.exploration_mode and main_rows > 0 and steps_run < max_steps:
        clarify = _exploration_clarify(brief, paths, row_counts)
        if clarify:
            return clarify

    if _is_impossible_analysis(brief, coverage, steps_run, main_rows, paths):
        return {
            "action": "impossible",
            "reason": "metric_not_mappable",
            "impossible_reason": "brief_metrics_not_found_in_dataset",
            "explanation_vi": "Không thể map metric từ brief sang cột dữ liệu sau khi chạy hết bước phân tích",
        }

    action = "complete"
    if coverage.diagnosis == "partial":
        action = "partial"

    payload: dict[str, Any] = {
        "action": action,
        "headline_metrics": metrics,
        "artifact_paths": artifacts,
        "caveats": coverage.gaps[:5],
        "sandbox_steps": steps_run,
        "coverage": coverage.model_dump(),
        "new_steps": [s.model_dump() for s in new_steps],
    }
    if new_steps:
        payload["analysis_script"] = new_steps[0].script_template
    return payload


def _coerce_plan(analysis_plan: AnalysisPlan | dict[str, Any] | None, brief: AnalysisBrief) -> AnalysisPlan:
    if analysis_plan is None:
        if brief.plan:
            return brief.plan
        from project_core.domain.analysis.decomposer import decompose_brief

        return decompose_brief(brief)
    if isinstance(analysis_plan, dict):
        return AnalysisPlan.model_validate(analysis_plan)
    return analysis_plan


def _resolve_execution(
    *,
    plan: AnalysisPlan,
    paths: list[str],
    meta: list[dict],
    brief: AnalysisBrief,
    analysis_tools: list[dict],
    recipe_candidates: list[dict],
    execution_plan: list[dict] | None,
) -> tuple[list[ExecutionStepPlan], ExecutionCoverage]:
    if execution_plan:
        steps = [ExecutionStepPlan.model_validate(s) for s in execution_plan]
        coverage = ExecutionCoverage(diagnosis="partial" if steps else "none")
        return steps, coverage

    candidates_by_subtask: dict[str, list[RecipeCandidate]] = {}
    for subtask in plan.subtasks:
        if recipe_candidates and recipe_candidates[0].get("subtask_id"):
            ranked = [
                RecipeCandidate.model_validate({k: v for k, v in c.items() if k != "subtask_id"})
                for c in recipe_candidates
                if c.get("subtask_id") == subtask.id
            ]
        else:
            ranked = rank_candidates(subtask.intent, analysis_tools, top_k=5)
        candidates_by_subtask[subtask.id] = ranked

    return build_execution_plan(
        plan,
        dataset_paths=paths,
        query_meta=meta,
        candidates_by_subtask=candidates_by_subtask,
        brief=brief,
    )


def _merge_external_paths(
    brief: AnalysisBrief,
    sql_paths: list[str],
    query_meta: list[dict[str, Any]],
) -> tuple[list[str], list[dict[str, Any]]]:
    paths = list(sql_paths)
    meta = list(query_meta)
    for ext in brief.external_sources or []:
        pp = ext.parquet_path or ext.path
        if pp and Path(pp).exists():
            paths.append(pp)
            meta.append(
                {
                    "role": "external",
                    "file_id": ext.file_id,
                    "source": ext.original_name,
                    "row_count": ext.row_count,
                }
            )
    return paths, meta


def _column_names(path: str) -> list[str]:
    try:
        import pandas as pd

        df = pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)
        return list(df.columns.astype(str))
    except Exception:
        return []


def _is_impossible_analysis(
    brief: AnalysisBrief,
    coverage: ExecutionCoverage,
    steps_run: int,
    main_rows: int,
    paths: list[str | None],
) -> bool:
    if main_rows <= 0:
        return False
    if coverage.diagnosis == "none" and steps_run == 0 and brief.metrics:
        primary = next((p for p in paths if p), None)
        if primary:
            cols = {c.lower() for c in _column_names(primary)}
            for metric in brief.metrics:
                if metric.lower() not in cols and metric.lower() not in {"revenue", "amount", "points"}:
                    return True
    if steps_run >= 1 and coverage.diagnosis == "none" and not coverage.gaps:
        return False
    budget_gaps = [g for g in coverage.gaps if g.startswith("budget_exceeded:")]
    if budget_gaps and steps_run >= 1 and not any(p for p in paths if p):
        return True
    return False


def _identifier_mismatch_feedback(
    product_code: str,
    probe_idxs: list[int],
    row_counts: dict[int, int],
    paths: list[str | None],
) -> dict[str, Any]:
    observed = "; ".join(f"probe_{i}={row_counts.get(i, 0)} rows" for i in probe_idxs)
    return {
        "action": "data_feedback",
        "data_feedback": DataFeedback(
            needs_sql_retry=True,
            issue="identifier_mismatch",
            diagnosis="needs_user_clarify",
            summary="Main query empty but product probe returned rows — likely wrong code format",
            suggested_intent_fix=f"Resolve product code for {product_code}",
            expected_vs_observed=[
                ExpectedVsObserved(
                    aspect="product_code",
                    expected=f"match for {product_code}",
                    observed=observed,
                )
            ],
            evidence_refs=[p for p in paths if p],
        ).model_dump(),
        "suggest_clarify": _product_clarify(product_code).model_dump(),
    }


def _empty_feedback(brief: AnalysisBrief, product_code: Any) -> dict[str, Any]:
    probes = []
    if product_code:
        probes = [
            ProbeRequest(
                table="SKU_DEF",
                purpose="sku_lookup",
                suggested_sql=(
                    f"SELECT TOP 5 SKU_ID, SKU_CODE, BARCODE FROM SKU_DEF "
                    f"WHERE SKU_CODE LIKE '%{product_code}%'"
                ),
            ),
            ProbeRequest(
                table="BARCODE",
                purpose="barcode_lookup",
                suggested_sql=(
                    f"SELECT TOP 5 BARCODE, SKU_ID FROM BARCODE WHERE BARCODE LIKE '%{product_code}%'"
                ),
            ),
        ]
    return {
        "action": "data_feedback",
        "data_feedback": DataFeedback(
            needs_sql_retry=True,
            issue="empty_result",
            diagnosis="needs_probe" if probes else "solvable",
            summary="No rows returned",
            suggested_intent_fix="expand filters or verify product code format",
            probe_requests=probes,
        ).model_dump(),
    }


def _product_clarify(product_code: str) -> ClarificationRequest:
    return ClarificationRequest(
        source_agent="IV",
        reason="product_code_ambiguous",
        trigger_context="after_data_feedback",
        partial_brief=AnalysisBrief(intent=f"product revenue {product_code}"),
        evidence_summary=f"Mã '{product_code}' không khớp trực tiếp; có kết quả từ bảng master/barcode",
        questions=[
            {
                "id": "product_code_choice",
                "prompt": f"Không tìm thấy doanh thu với mã '{product_code}'. Bạn muốn dùng cách tra cứu nào?",
                "options": [
                    {
                        "id": "try_barcode",
                        "label": "Tra theo mã vạch / barcode đầy đủ",
                        "brief_value": {"filters": {"lookup_mode": "barcode"}},
                    },
                    {
                        "id": "try_sku_pad",
                        "label": "Thêm số 0 đầu (mã nội bộ 8 số)",
                        "brief_value": {"filters": {"lookup_mode": "sku_padded"}},
                    },
                    {
                        "id": "unknown",
                        "label": "Tôi không chắc — hãy khám phá dữ liệu giúp tôi",
                        "brief_value": {"exploration_mode": True, "user_knowledge_level": "unknown"},
                    },
                ],
                "maps_to_brief_field": "filters.lookup_mode",
            }
        ],
    )


def _exploration_clarify(
    brief: AnalysisBrief,
    paths: list[str | None],
    row_counts: dict[int, int],
) -> dict[str, Any] | None:
    if brief.user_knowledge_level != "unknown":
        return None
    sample_evidence = json.dumps({str(i): row_counts.get(i, 0) for i in row_counts}, ensure_ascii=False)
    req = ClarificationRequest(
        source_agent="IV",
        reason="exploration_needs_direction",
        trigger_context="after_data_feedback",
        partial_brief=brief,
        evidence_summary=f"Đã lấy mẫu dữ liệu: {sample_evidence}",
        questions=[
            {
                "id": "exploration_focus",
                "prompt": "Dữ liệu đã được tải. Bạn muốn tập trung vào khía cạnh nào?",
                "options": [
                    {"id": "revenue", "label": "Doanh thu / số lượng bán", "brief_value": {"metrics": ["revenue"]}},
                    {"id": "trend", "label": "Xu hướng theo thời gian", "brief_value": {"dimensions": ["time"]}},
                    {"id": "unknown", "label": "Tiếp tục khám phá tự động", "brief_value": {"exploration_mode": True}},
                ],
                "maps_to_brief_field": "metrics",
            }
        ],
    )
    return {"action": "suggest_clarify", "clarification_request": req.model_dump()}
