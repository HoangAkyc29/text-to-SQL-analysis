from __future__ import annotations

import json
import os
import re
from uuid import uuid4

from project_core.domain.contracts.analysis_plan import AnalysisPlan, AnalysisSubtask
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.llm.openrouter_client import OpenRouterClient
from project_core.models.loader import agent_profile


_ASPECT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "revenue": ("doanh thu", "revenue", "bán", "sales", "amount"),
    "vip": ("vip", "thẻ", "card", "loyalty"),
    "inventory": ("tồn kho", "inventory", "stock", "onhand"),
    "trend": ("xu hướng", "trend", "theo tháng", "monthly", "q1", "q2"),
    "compare": ("so sánh", "compare", "vs", "đối chiếu"),
    "topn": ("top", "cao nhất", "rank"),
    "store": ("cửa hàng", "store", "stk", "chi nhánh"),
    "product": ("sku", "mã hàng", "barcode", "sản phẩm"),
}


def decompose_brief(brief: AnalysisBrief, *, min_tokens_for_split: int = 12, use_llm: bool | None = None) -> AnalysisPlan:
    """Split macro intents into subtasks (LLM when available, else heuristic)."""
    if use_llm is None:
        use_llm = os.getenv("ALLOW_LLM_STUB") != "1"
    if use_llm:
        try:
            return decompose_brief_llm(brief)
        except Exception:
            pass
    return decompose_brief_heuristic(brief, min_tokens_for_split=min_tokens_for_split)


def decompose_brief_llm(brief: AnalysisBrief) -> AnalysisPlan:
    if os.getenv("ALLOW_LLM_STUB") == "1":
        return decompose_brief_heuristic(brief)

    client = OpenRouterClient()
    payload = {
        "intent": brief.intent,
        "metrics": brief.metrics,
        "dimensions": brief.dimensions,
        "filters": brief.filters,
        "time_range": brief.time_range.model_dump(),
    }
    result = client.chat(
        profile_name=agent_profile("router"),
        messages=[
            {
                "role": "system",
                "content": (
                    "Decompose supermarket analysis intent into subtasks. "
                    'Return JSON: {"is_decomposed": bool, "subtasks": [{"id": str, "intent": str, '
                    '"metrics": [], "dimensions": [], "filters": {}}]}'
                ),
            },
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        response_format={"type": "json_object"},
    )
    data = json.loads(result.content)
    subtasks = [
        AnalysisSubtask(
            id=str(s.get("id") or f"st-llm-{i}"),
            intent=str(s.get("intent") or brief.intent),
            metrics=list(s.get("metrics") or brief.metrics),
            dimensions=list(s.get("dimensions") or brief.dimensions),
            filters={**(brief.filters or {}), **(s.get("filters") or {})},
        )
        for i, s in enumerate(data.get("subtasks") or [])
    ]
    if not subtasks:
        return decompose_brief_heuristic(brief)
    return AnalysisPlan(subtasks=subtasks, is_decomposed=bool(data.get("is_decomposed", len(subtasks) > 1)))


def decompose_brief_heuristic(brief: AnalysisBrief, *, min_tokens_for_split: int = 12) -> AnalysisPlan:
    """Heuristic split when multiple analytic aspects are detected."""
    intent = (brief.intent or "").strip()
    if not intent:
        return AnalysisPlan(subtasks=[_single_subtask(brief)], is_decomposed=False)

    lower = intent.lower()
    detected = [aspect for aspect, kws in _ASPECT_KEYWORDS.items() if any(k in lower for k in kws)]

    if len(detected) <= 1 and len(intent.split()) < min_tokens_for_split:
        return AnalysisPlan(subtasks=[_single_subtask(brief)], is_decomposed=False)

    if len(detected) <= 1:
        parts = _split_clauses(intent)
        if len(parts) <= 1:
            return AnalysisPlan(subtasks=[_single_subtask(brief)], is_decomposed=False)
        subtasks = [_subtask_from_clause(p, brief, i) for i, p in enumerate(parts)]
        return AnalysisPlan(subtasks=subtasks, is_decomposed=True)

    subtasks: list[AnalysisSubtask] = []
    for i, aspect in enumerate(detected):
        subtasks.append(
            AnalysisSubtask(
                id=f"st-{aspect}-{i}",
                intent=f"{intent} — focus {aspect}",
                metrics=_metrics_for_aspect(aspect, brief),
                dimensions=_dimensions_for_aspect(aspect, brief),
                filters=dict(brief.filters),
            )
        )
    return AnalysisPlan(subtasks=subtasks, is_decomposed=True)


def _single_subtask(brief: AnalysisBrief) -> AnalysisSubtask:
    return AnalysisSubtask(
        id="st-main",
        intent=brief.intent,
        metrics=list(brief.metrics),
        dimensions=list(brief.dimensions),
        filters=dict(brief.filters),
    )


def _split_clauses(intent: str) -> list[str]:
    parts = re.split(r"[,;]|\s+và\s+|\s+and\s+", intent, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]


def _subtask_from_clause(clause: str, brief: AnalysisBrief, index: int) -> AnalysisSubtask:
    return AnalysisSubtask(
        id=f"st-clause-{index}",
        intent=clause,
        metrics=list(brief.metrics),
        dimensions=list(brief.dimensions),
        filters=dict(brief.filters),
    )


def _metrics_for_aspect(aspect: str, brief: AnalysisBrief) -> list[str]:
    if brief.metrics:
        return list(brief.metrics)
    return {"revenue": ["revenue"], "vip": ["revenue"], "inventory": ["inventory"]}.get(aspect, [])


def _dimensions_for_aspect(aspect: str, brief: AnalysisBrief) -> list[str]:
    if brief.dimensions:
        return list(brief.dimensions)
    return {
        "trend": ["time"],
        "store": ["store"],
        "product": ["product"],
        "compare": ["time"],
    }.get(aspect, [])
