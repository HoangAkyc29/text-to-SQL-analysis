from __future__ import annotations

from typing import Any

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
) -> list[RecipeCandidate]:
    if not tools:
        return []

    token_ranked = {c.tool_id: c for c in rank_candidates(intent, tools, top_k=len(tools))}
    embed_scores: dict[str, float] = {}
    if query_embedding:
        for tool in tools:
            emb = tool.get("embedding") or []
            embed_scores[str(tool.get("tool_id", ""))] = _cosine(query_embedding, emb) if emb else 0.0

    merged: list[RecipeCandidate] = []
    for tool in tools:
        tid = str(tool.get("tool_id", ""))
        base = token_ranked.get(tid) or tool_to_candidate(intent, tool)
        embed_score = embed_scores.get(tid, 0.0)
        hybrid = token_weight * base.score + embed_weight * embed_score
        merged.append(
            base.model_copy(
                update={
                    "score": round(hybrid, 4),
                    "matched_aspects": base.matched_aspects + ([f"embed:{embed_score:.2f}"] if embed_score else []),
                }
            )
        )
    merged.sort(key=lambda c: c.score, reverse=True)
    return merged[:top_k]
