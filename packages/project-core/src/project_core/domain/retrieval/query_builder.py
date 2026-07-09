from __future__ import annotations

from typing import Any

from project_core.domain.contracts.brief import AnalysisBrief


def build_retrieval_query(intent: str, brief: AnalysisBrief | dict[str, Any] | None = None) -> str:
    """Enrich vector query from intent + brief filters."""
    parts = [intent.strip()] if intent else []
    if brief is None:
        return " ".join(parts)
    data = brief.model_dump() if hasattr(brief, "model_dump") else dict(brief)
    filters = data.get("filters") or {}
    for key in ("product_code", "min_bill_value", "min_transaction_value", "card_prefix", "STK_ID"):
        val = filters.get(key)
        if val is not None:
            parts.append(f"{key}={val}")
    tr = data.get("time_range") or {}
    if tr.get("start"):
        parts.append(f"from {tr['start']}")
    if tr.get("end"):
        parts.append(f"to {tr['end']}")
    metrics = data.get("metrics") or []
    if metrics:
        parts.append("metrics:" + ",".join(str(m) for m in metrics))
    return " ".join(parts)
