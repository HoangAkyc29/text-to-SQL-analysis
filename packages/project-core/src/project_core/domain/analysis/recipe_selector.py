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
    if candidate.steps:
        step = candidate.steps[0].model_copy()
        step.params = {**step.params, **params}
        step.source_tool_id = candidate.tool_id
        step.status = "reuse"
        return step
    return RecipeStep(
        step_id=f"{candidate.tool_id}-main",
        name=candidate.name,
        script_template=candidate.script_template,
        source_tool_id=candidate.tool_id,
        params=params,
        param_schema=candidate.param_schema,
        status="reuse",
    )
