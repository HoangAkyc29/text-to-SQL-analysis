from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from project_core.domain.contracts.analysis_plan import (
    AnalysisPlan,
    AnalysisSubtask,
    ExecutionCoverage,
    ExecutionStepPlan,
    RecipeCandidate,
    RecipeStep,
)
from project_core.domain.analysis.param_resolver import resolve_params
from project_core.domain.analysis.recipe_selector import candidate_to_step, select_recipe_for_subtask
from project_core.domain.contracts.brief import AnalysisBrief


def build_execution_plan(
    plan: AnalysisPlan,
    *,
    dataset_paths: list[str],
    query_meta: list[dict],
    candidates_by_subtask: dict[str, list[RecipeCandidate]],
    brief: AnalysisBrief | None = None,
    min_reuse_score: float = 0.35,
) -> tuple[list[ExecutionStepPlan], ExecutionCoverage]:
    steps_out: list[ExecutionStepPlan] = []
    reused: list[str] = []
    generated: list[str] = []
    gaps: list[str] = []
    subtask_status: dict[str, str] = {}

    for subtask in plan.subtasks:
        path = _path_for_subtask(subtask, dataset_paths, query_meta)
        candidates = candidates_by_subtask.get(subtask.id) or []
        chosen, params, _rationale = (None, resolve_params(brief, subtask) if brief else {}, "no_brief")
        if brief and candidates:
            chosen, params, _rationale = select_recipe_for_subtask(
                brief=brief, subtask=subtask, candidates=candidates
            )
        best = chosen or (candidates[0] if candidates else None)
        reuse_score = best.score if best else 0.0
        can_reuse = bool(best and (chosen or reuse_score >= min_reuse_score) and best.steps)

        if can_reuse and best:
            step = candidate_to_step(best, params)
            steps_out.append(
                ExecutionStepPlan(
                    subtask_id=subtask.id,
                    step=step,
                    dataset_path=path,
                    candidate_tool_id=best.tool_id,
                    match_score=best.score,
                )
            )
            reused.append(f"recipe:{best.tool_id}@{best.score}")
            if best.missing_aspects:
                gaps.extend([f"{subtask.id}:{a}" for a in best.missing_aspects[:3]])
            subtask_status[subtask.id] = "partial_reuse" if best.missing_aspects else "reuse"
        else:
            gen = _generated_step_for_subtask(subtask, params)
            steps_out.append(
                ExecutionStepPlan(
                    subtask_id=subtask.id,
                    step=gen,
                    dataset_path=path,
                    match_score=best.score if best else 0.0,
                )
            )
            generated.append(f"step:{gen.step_id}")
            if best and best.score > 0:
                gaps.append(f"{subtask.id}:weak_match:{best.score}")
            else:
                gaps.append(f"{subtask.id}:no_recipe")
            subtask_status[subtask.id] = "generated"

    diagnosis = "full"
    if generated and reused:
        diagnosis = "partial"
    elif gaps and generated:
        diagnosis = "partial"

    coverage = ExecutionCoverage(
        diagnosis=diagnosis,
        reused=reused,
        generated=generated,
        gaps=gaps,
        subtask_status=subtask_status,
    )
    return steps_out, coverage


def _path_for_subtask(
    subtask: AnalysisSubtask,
    paths: list[str],
    query_meta: list[dict],
) -> str:
    if subtask.dataset_query_index is not None and subtask.dataset_query_index < len(paths):
        return paths[subtask.dataset_query_index]
    for i, meta in enumerate(query_meta):
        if meta.get("subtask_id") == subtask.id and i < len(paths):
            return paths[i]
    return paths[0] if paths else ""


def _generated_step_for_subtask(subtask: AnalysisSubtask, params: dict | None = None) -> RecipeStep:
    params = params or {}
    group_cols = subtask.dimensions or [params.get("group_by") or "month"]
    group_expr = ", ".join(f"'{c}'" for c in group_cols if c)
    metric = params.get("metric", "AMOUNT")
    card_prefix = params.get("card_prefix")
    filter_line = ""
    if card_prefix:
        filter_line = f"df = df[df['CARD_NO'].astype(str).str.startswith({json.dumps(card_prefix)})]"
    return RecipeStep(
        step_id=str(uuid4()),
        name=f"generated_{subtask.id}",
        status="generated",
        params=params,
        script_template=f"""
df = pd.read_parquet(path) if str(path).endswith('.parquet') else pd.read_csv(path)
{filter_line}
group_cols = [{group_expr}]
cols = [c for c in group_cols if c in df.columns]
metric = {json.dumps(metric)}
if cols and metric in df.columns:
    agg = df.groupby(cols)[metric].sum().reset_index()
else:
    agg = df.describe(include='all').transpose()
agg.to_csv(out / '{subtask.id}_summary.csv')
""",
    )
