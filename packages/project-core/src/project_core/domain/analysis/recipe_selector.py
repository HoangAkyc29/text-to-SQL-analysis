from __future__ import annotations

import json
import os
from typing import Any

from pathlib import Path

from project_core.domain.analysis.param_resolver import apply_param_schema_defaults, resolve_params
from project_core.domain.contracts.analysis_plan import AnalysisSubtask, RecipeCandidate, RecipeStep
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.llm.openrouter_client import OpenRouterClient
from project_core.models.loader import agent_profile


def _analysis_prompt(name: str) -> str:
    path = Path(__file__).resolve().parent / "prompts" / f"{name}.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def select_recipe_for_subtask(
    *,
    brief: AnalysisBrief,
    subtask: AnalysisSubtask,
    candidates: list[RecipeCandidate],
) -> tuple[RecipeCandidate | None, dict[str, Any], str]:
    """Pick best recipe + params. Returns (candidate, params, rationale)."""
    if not candidates:
        return None, resolve_params(brief, subtask), "no_candidates"

    if os.getenv("ALLOW_LLM_STUB") == "1":
        return _select_stub(brief, subtask, candidates)

    try:
        return _select_llm(brief, subtask, candidates)
    except Exception:
        return _select_stub(brief, subtask, candidates)


def _select_stub(
    brief: AnalysisBrief,
    subtask: AnalysisSubtask,
    candidates: list[RecipeCandidate],
) -> tuple[RecipeCandidate | None, dict[str, Any], str]:
    best = candidates[0]
    if best.score < 0.2:
        return None, resolve_params(brief, subtask), "score_below_threshold"
    params = resolve_params(brief, subtask)
    params = apply_param_schema_defaults([p.model_dump() for p in best.param_schema], params)
    return best, params, f"stub_top1 score={best.score}"


def _select_llm(
    brief: AnalysisBrief,
    subtask: AnalysisSubtask,
    candidates: list[RecipeCandidate],
) -> tuple[RecipeCandidate | None, dict[str, Any], str]:
    client = OpenRouterClient()
    payload = {
        "subtask": subtask.model_dump(),
        "brief": brief.model_dump(),
        "candidates": [
            {
                "tool_id": c.tool_id,
                "name": c.name,
                "score": c.score,
                "matched": c.matched_aspects,
                "missing": c.missing_aspects,
                "params_schema": [p.model_dump() for p in c.param_schema],
            }
            for c in candidates[:5]
        ],
    }
    result = client.chat(
        profile_name=agent_profile("analyst"),
        messages=[
            {"role": "system", "content": _analysis_prompt("recipe_select_guide")},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        response_format={"type": "json_object"},
    )
    data = json.loads(result.content)
    if data.get("use_none") or not data.get("tool_id"):
        params = resolve_params(brief, subtask)
        return None, params, str(data.get("rationale", "llm_skip"))

    tool_id = str(data["tool_id"])
    chosen = next((c for c in candidates if c.tool_id == tool_id), candidates[0])
    params = {**resolve_params(brief, subtask), **(data.get("params") or {})}
    params = apply_param_schema_defaults([p.model_dump() for p in chosen.param_schema], params)
    return chosen, params, str(data.get("rationale", "llm_selected"))


def candidate_to_step(candidate: RecipeCandidate, params: dict[str, Any]) -> RecipeStep:
    steps = candidate_to_steps(candidate, params)
    if steps:
        return steps[0]
    return RecipeStep(
        step_id=f"{candidate.tool_id}-main",
        name=candidate.name,
        script_template=candidate.script_template,
        source_tool_id=candidate.tool_id,
        params=params,
        param_schema=candidate.param_schema,
        status="reuse",
    )


def candidate_to_steps(
    candidate: RecipeCandidate, params: dict[str, Any]
) -> list[RecipeStep]:
    """Preserve the full reusable catalog chain instead of truncating to step one."""
    source_steps = candidate.steps
    if candidate.op_chain:
        source_steps = [
            RecipeStep(
                step_id=f"{candidate.tool_id}-op-{index}-{raw.get('op_id', 'unknown')}",
                name=str(raw.get("op_id") or "catalog_op"),
                op_id=str(raw.get("op_id") or ""),
                args=dict(raw.get("args") or {}),
                dataset=raw.get("dataset"),
                save_as=raw.get("save_as"),
                source_tool_id=candidate.tool_id,
                status="reuse",
            )
            for index, raw in enumerate(candidate.op_chain)
            if isinstance(raw, dict) and raw.get("op_id")
        ]
    out: list[RecipeStep] = []
    for source in source_steps:
        step = source.model_copy(deep=True)
        step.params = {**step.params, **params}
        step.source_tool_id = candidate.tool_id
        step.status = "reuse"
        out.append(step)
    return out
