from __future__ import annotations

import re
from typing import Any

from project_core.domain.contracts.brief import AnalysisBrief

# Filter keys that are useful as *type* tokens for embedding — never dump raw values (SKUs, amounts).
_FILTER_TYPE_TOKENS = (
    "product_code",
    "sku",
    "min_bill_value",
    "min_transaction_value",
    "card_prefix",
    "STK_ID",
)

_DIGIT_RUN = re.compile(r"\d{5,}")
_MAX_FACETS = 8


def sanitize_retrieval_text(text: str) -> str:
    """Strip long digit runs (SKU/PLU/amounts) before embedding."""
    cleaned = _DIGIT_RUN.sub(" ", text or "")
    return " ".join(cleaned.split())


def build_retrieval_query(intent: str, brief: AnalysisBrief | dict[str, Any] | None = None) -> str:
    """Enrich vector query from intent + brief — domain tokens only, no raw ids/amounts."""
    parts = [sanitize_retrieval_text(intent.strip())] if intent else []
    if brief is None:
        return " ".join(p for p in parts if p)
    data = brief.model_dump() if hasattr(brief, "model_dump") else dict(brief)
    filters = data.get("filters") or {}
    for key in _FILTER_TYPE_TOKENS:
        if filters.get(key) is not None:
            parts.append(key)
    tr = data.get("time_range") or {}
    if tr.get("start") or tr.get("end") or tr.get("from") or tr.get("to"):
        parts.append("date_range")
    metrics = data.get("metrics") or []
    if metrics:
        parts.append("metrics:" + ",".join(str(m) for m in metrics))
    return " ".join(p for p in parts if p)


def _fallback_facets(data: dict[str, Any]) -> list[str]:
    facets: list[str] = []
    tr = data.get("time_range") or {}
    if tr.get("start") or tr.get("end") or tr.get("from") or tr.get("to"):
        facets.append("Phân tích theo khoảng thời gian giao dịch")
    filters = data.get("filters") or {}
    if filters.get("product_code") is not None or filters.get("sku") is not None:
        facets.append("Lọc theo mã hàng / SKU hiển thị trên master sản phẩm")
    if filters.get("min_bill_value") is not None or filters.get("min_transaction_value") is not None:
        facets.append("Lọc theo tổng giá trị bill tối thiểu trên header bill")
    metrics = [str(m).lower() for m in (data.get("metrics") or [])]
    if any(m in {"qty", "quantity"} or "qty" in m or "quantity" in m for m in metrics):
        facets.append("Đo số lượng trên dòng bán")
    if any(m in {"revenue", "amount"} or "revenue" in m for m in metrics):
        facets.append("Đo doanh thu / thành tiền giao dịch")
    return facets


def build_retrieval_facets(brief: AnalysisBrief | dict[str, Any] | None = None) -> list[str]:
    """Independent retrieval sentences from brief.retrieval_facets or structural fallback."""
    if brief is None:
        return []
    data = brief.model_dump() if hasattr(brief, "model_dump") else dict(brief)
    raw = [str(x).strip() for x in (data.get("retrieval_facets") or []) if str(x).strip()]
    facets = [sanitize_retrieval_text(f) for f in raw]
    facets = [f for f in facets if f][:_MAX_FACETS]
    if facets:
        return facets
    return [sanitize_retrieval_text(f) for f in _fallback_facets(data) if f][:_MAX_FACETS]
