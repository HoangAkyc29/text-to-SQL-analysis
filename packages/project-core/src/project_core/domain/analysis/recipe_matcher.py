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
    op_chain = _op_chain_from_tool(tool)
    params_raw = (tool.get("input_schema") or {}).get("params") or []
    params: list[RecipeParam] = []
    for p in params_raw:
        try:
            params.append(RecipeParam.model_validate(p))
        except Exception:
            continue
    return RecipeCandidate(
        tool_id=str(tool.get("tool_id", "")),
        name=str(tool.get("name", "")),
        intent_pattern=str(tool.get("intent_pattern", "")),
        score=round(score, 4),
        matched_aspects=matched,
        missing_aspects=missing,
        steps=steps,
        op_chain=op_chain,
        script_template=str(tool.get("script_template") or ""),
        param_schema=params,
    )


def rank_candidates(intent: str, tools: list[dict[str, Any]], *, top_k: int = 5) -> list[RecipeCandidate]:
    ranked = [tool_to_candidate(intent, t) for t in tools]
    ranked.sort(key=lambda c: c.score, reverse=True)
    return [c for c in ranked if c.score > 0.05][:top_k]


def _op_chain_from_tool(tool: dict[str, Any]) -> list[dict[str, Any]]:
    raw = tool.get("op_chain") or tool.get("steps") or []
    out: list[dict[str, Any]] = []
    for s in raw:
        if not isinstance(s, dict) or not s.get("op_id"):
            continue
        # Skip observation-like crumbs (e.g. {"op_id":"cast_column","status":"ok"})
        if s.get("status") in {"ok", "error"} and "args" not in s and "dataset" not in s:
            continue
        out.append(
            {
                "op_id": str(s["op_id"]),
                "args": dict(s.get("args") or {}),
                **({"dataset": s["dataset"]} if s.get("dataset") else {}),
                **({"save_as": s["save_as"]} if s.get("save_as") else {}),
            }
        )
    return out


def _steps_from_tool(tool: dict[str, Any]) -> list[RecipeStep]:
    """Parse steps from tool record; never raise on mixed/legacy Mongo shapes."""
    op_chain = _op_chain_from_tool(tool)
    if op_chain:
        return [
            RecipeStep(
                step_id=f"{tool.get('tool_id', 'tool')}-op-{i}-{step['op_id']}",
                name=str(step["op_id"]),
                op_id=str(step["op_id"]),
                args=dict(step.get("args") or {}),
                dataset=step.get("dataset"),
                save_as=step.get("save_as"),
                source_tool_id=str(tool.get("tool_id") or ""),
                status="reuse",
            )
            for i, step in enumerate(op_chain)
        ]

    raw_steps = tool.get("steps") or []
    parsed: list[RecipeStep] = []
    for i, s in enumerate(raw_steps):
        if not isinstance(s, dict):
            continue
        # Ignore IV observation crumbs that were mistakenly staged
        st = s.get("status")
        if st in {"ok", "error"} and not s.get("step_id") and not s.get("script_template"):
            continue
        if s.get("op_id") and not s.get("script_template"):
            parsed.append(
                RecipeStep(
                    step_id=str(s.get("step_id") or f"{tool.get('tool_id', 'tool')}-op-{i}"),
                    name=str(s.get("name") or s["op_id"]),
                    op_id=str(s["op_id"]),
                    args=dict(s.get("args") or {}),
                    dataset=s.get("dataset"),
                    save_as=s.get("save_as"),
                    source_tool_id=str(tool.get("tool_id") or ""),
                    status="reuse",
                )
            )
            continue
        try:
            parsed.append(RecipeStep.model_validate(s))
        except Exception:
            continue
    if parsed:
        return parsed

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
