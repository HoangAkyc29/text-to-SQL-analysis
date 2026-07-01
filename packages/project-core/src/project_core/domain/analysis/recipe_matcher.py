from __future__ import annotations

import re
from typing import Any

from project_core.domain.contracts.analysis_plan import RecipeCandidate, RecipeParam, RecipeStep


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z0-9_àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+", text.lower()) if len(t) > 2}


def score_recipe_against_intent(intent: str, tool: dict[str, Any]) -> tuple[float, list[str], list[str]]:
    """Token overlap score with matched/missing aspect hints."""
    intent_tokens = _tokenize(intent)
    pattern = tool.get("intent_pattern") or tool.get("name") or ""
    recipe_tokens = _tokenize(pattern)
    if not intent_tokens:
        return 0.0, [], list(recipe_tokens)

    matched = intent_tokens & recipe_tokens
    extra_in_recipe = recipe_tokens - intent_tokens
    missing_in_recipe = intent_tokens - recipe_tokens

    if not recipe_tokens:
        return 0.1, [], list(intent_tokens)

    precision = len(matched) / max(len(recipe_tokens), 1)
    recall = len(matched) / max(len(intent_tokens), 1)
    score = 0.6 * recall + 0.4 * precision
    return score, sorted(matched), sorted(missing_in_recipe)[:8]


def tool_to_candidate(intent: str, tool: dict[str, Any]) -> RecipeCandidate:
    score, matched, missing = score_recipe_against_intent(intent, tool)
    steps = _steps_from_tool(tool)
    params = [RecipeParam.model_validate(p) for p in (tool.get("input_schema") or {}).get("params") or []]
    return RecipeCandidate(
        tool_id=str(tool.get("tool_id", "")),
        name=str(tool.get("name", "")),
        intent_pattern=str(tool.get("intent_pattern", "")),
        score=round(score, 4),
        matched_aspects=matched,
        missing_aspects=missing,
        steps=steps,
        script_template=str(tool.get("script_template") or ""),
        param_schema=params,
    )


def rank_candidates(intent: str, tools: list[dict[str, Any]], *, top_k: int = 5) -> list[RecipeCandidate]:
    ranked = [tool_to_candidate(intent, t) for t in tools]
    ranked.sort(key=lambda c: c.score, reverse=True)
    return [c for c in ranked if c.score > 0.05][:top_k]


def _steps_from_tool(tool: dict[str, Any]) -> list[RecipeStep]:
    raw_steps = tool.get("steps") or []
    if raw_steps:
        return [RecipeStep.model_validate(s) for s in raw_steps]
    script = tool.get("script_template") or ""
    if not script:
        return []
    return [
        RecipeStep(
            step_id=f"{tool.get('tool_id', 'tool')}-main",
            name=str(tool.get("name") or "main"),
            script_template=script,
            source_tool_id=str(tool.get("tool_id") or ""),
            status="reuse",
        )
    ]
