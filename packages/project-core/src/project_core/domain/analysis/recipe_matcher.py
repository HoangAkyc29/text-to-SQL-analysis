from __future__ import annotations

import re
from typing import Any

from project_core.domain.analysis.recipe_binding import canonicalize_op_chain
from project_core.domain.contracts.analysis_plan import (
    RecipeCandidate,
    RecipeDatasetContract,
    RecipeParam,
    RecipeStep,
    RecipeVerificationContract,
)


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
    dataset_contracts: list[RecipeDatasetContract] = []
    for contract in tool.get("dataset_contracts") or []:
        try:
            dataset_contracts.append(RecipeDatasetContract.model_validate(contract))
        except Exception:
            continue
    try:
        verification = RecipeVerificationContract.model_validate(
            tool.get("verification_contract") or {}
        )
    except Exception:
        verification = RecipeVerificationContract()
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
        dataset_contracts=dataset_contracts,
        verification_contract=verification,
        compatibility_version=int(tool.get("compatibility_version") or 0),
        compatibility_status=(
            "compatible"
            if tool.get("kind") == "catalog_op_chain"
            and int(tool.get("compatibility_version") or 0) == 2
            else "incompatible"
        ),
        rejection_reasons=(
            [] if int(tool.get("compatibility_version") or 0) == 2
            else ["recipe_not_canonical_v2"]
        ),
    )


def rank_candidates(intent: str, tools: list[dict[str, Any]], *, top_k: int = 5) -> list[RecipeCandidate]:
    ranked = [tool_to_candidate(intent, t) for t in tools]
    ranked.sort(key=lambda c: c.score, reverse=True)
    return [c for c in ranked if c.score > 0.05][:top_k]


def _op_chain_from_tool(tool: dict[str, Any]) -> list[dict[str, Any]]:
    if tool.get("kind") != "catalog_op_chain":
        return []
    return canonicalize_op_chain(tool.get("op_chain"))


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
                dataset=(step.get("args") or {}).get("dataset"),
                save_as=(step.get("args") or {}).get("save_as"),
                source_tool_id=str(tool.get("tool_id") or ""),
                status="reuse",
            )
            for i, step in enumerate(op_chain)
        ]

    # Legacy script records are intentionally not adapted into recipe-v2.
    raw_steps: list[dict[str, Any]] = []
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

    return []
