from __future__ import annotations

from typing import Any

from project_core.domain.analysis.recipe_binding import bind_and_preflight, is_recipe_v2
from project_core.domain.analysis.recipe_matcher import rank_candidates, tool_to_candidate
from project_core.domain.contracts.analysis_plan import RecipeCandidate
from project_core.domain.retrieval.mongo_vector import _cosine


def hybrid_rank_candidates(
    intent: str,
    tools: list[dict[str, Any]],
    *,
    query_embedding: list[float] | None = None,
    top_k: int = 5,
    token_weight: float = 0.45,
    embed_weight: float = 0.55,
    datasets: list[dict[str, Any]] | None = None,
    params: dict[str, Any] | None = None,
    available_ops: set[str] | None = None,
    min_score: float = 0.0,
    rejected: list[RecipeCandidate] | None = None,
) -> list[RecipeCandidate]:
    if not tools:
        return []

    canonical_tools = [tool for tool in tools if is_recipe_v2(tool)]
    for tool in tools:
        if tool in canonical_tools:
            continue
        candidate = tool_to_candidate(intent, tool).model_copy(
            update={
                "compatibility_status": "incompatible",
                "rejection_reasons": ["recipe_not_canonical_v2"],
            }
        )
        if rejected is not None:
            rejected.append(candidate)
    token_ranked = {
        c.tool_id: c
        for c in rank_candidates(intent, canonical_tools, top_k=len(canonical_tools))
    }
    embed_scores: dict[str, float] = {}
    if query_embedding:
        for tool in canonical_tools:
            emb = tool.get("embedding") or []
            embed_scores[str(tool.get("tool_id", ""))] = _cosine(query_embedding, emb) if emb else 0.0

    merged: list[RecipeCandidate] = []
    for tool in canonical_tools:
        tid = str(tool.get("tool_id", ""))
        base = token_ranked.get(tid) or tool_to_candidate(intent, tool)
        embed_score = embed_scores.get(tid, 0.0)
        hybrid = token_weight * base.score + embed_weight * embed_score
        candidate = base.model_copy(
            update={
                "score": round(hybrid, 4),
                "matched_aspects": base.matched_aspects
                + ([f"embed:{embed_score:.2f}"] if embed_score else []),
            }
        )
        if candidate.score < min_score:
            candidate = candidate.model_copy(
                update={
                    "compatibility_status": "incompatible",
                    "rejection_reasons": [f"score_below_threshold:{min_score}"],
                }
            )
            if rejected is not None:
                rejected.append(candidate)
            continue
        if datasets is not None:
            check = bind_and_preflight(
                tool,
                datasets,
                params=params,
                available_ops=available_ops,
            )
            candidate = candidate.model_copy(
                update={
                    "compatibility_status": (
                        "compatible" if check.compatible else "incompatible"
                    ),
                    "rejection_reasons": check.rejection_reasons,
                    "dataset_bindings": check.dataset_bindings,
                    "op_chain": check.op_chain,
                }
            )
            if not check.compatible:
                if rejected is not None:
                    rejected.append(candidate)
                continue
        merged.append(candidate)
    merged.sort(key=lambda c: c.score, reverse=True)
    return merged[:top_k]
