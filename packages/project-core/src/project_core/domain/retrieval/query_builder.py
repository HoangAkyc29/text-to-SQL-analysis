from __future__ import annotations

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

_MAX_FACETS = 8

# Structural facet texts (meta, keyed off brief filter presence — not skill recipes).
_PRODUCT_CODE_FACET = "Lọc theo mã hàng / SKU hiển thị trên master sản phẩm"
_MIN_BILL_FACET = "Lọc theo tổng giá trị bill tối thiểu trên header bill"
_TIME_FACET = "Phân tích theo khoảng thời gian giao dịch"
_QTY_FACET = "Đo số lượng trên dòng bán"
_REVENUE_FACET = "Đo doanh thu / thành tiền giao dịch"


def sanitize_retrieval_text(text: str) -> str:
    """Normalize whitespace only — keep digit codes/amounts for embedding."""
    return " ".join((text or "").split())


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
        facets.append(_TIME_FACET)
    filters = data.get("filters") or {}
    if filters.get("product_code") is not None or filters.get("sku") is not None:
        facets.append(_PRODUCT_CODE_FACET)
    if filters.get("min_bill_value") is not None or filters.get("min_transaction_value") is not None:
        facets.append(_MIN_BILL_FACET)
    metrics = [str(m).lower() for m in (data.get("metrics") or [])]
    if any(m in {"qty", "quantity"} or "qty" in m or "quantity" in m for m in metrics):
        facets.append(_QTY_FACET)
    if any(m in {"revenue", "amount"} or "revenue" in m for m in metrics):
        facets.append(_REVENUE_FACET)
    return facets


def _facet_covers_product_code_filter(text: str) -> bool:
    """Heuristic: LLM already wrote a product-code / SKU filter facet."""
    lowered = (text or "").lower()
    needles = (
        "mã hàng",
        "ma hang",
        "mã sản phẩm",
        "ma san pham",
        "product_code",
        "sku",
        "lọc theo mã",
        "loc theo ma",
        "master sản phẩm",
        "master san pham",
    )
    return any(n in lowered for n in needles)


def build_retrieval_facets(brief: AnalysisBrief | dict[str, Any] | None = None) -> list[str]:
    """Merge Agent I facets with structural fallbacks required by brief filters.

    When Agent I fills ``retrieval_facets`` but omits an active filter type
    (common on follow-ups), still append the matching structural facet so
    schema RAG is not starved of that constraint signal.
    """
    if brief is None:
        return []
    data = brief.model_dump() if hasattr(brief, "model_dump") else dict(brief)
    raw = [str(x).strip() for x in (data.get("retrieval_facets") or []) if str(x).strip()]
    llm_facets = [sanitize_retrieval_text(f) for f in raw]
    llm_facets = [f for f in llm_facets if f]

    structural = [sanitize_retrieval_text(f) for f in _fallback_facets(data) if f]
    filters = data.get("filters") or {}
    needs_product = filters.get("product_code") is not None or filters.get("sku") is not None

    merged: list[str] = []
    seen: set[str] = set()

    def _add(item: str) -> None:
        key = item.casefold()
        if not item or key in seen:
            return
        seen.add(key)
        merged.append(item)

    if needs_product and not any(_facet_covers_product_code_filter(f) for f in llm_facets):
        _add(_PRODUCT_CODE_FACET)

    for item in llm_facets:
        _add(item)

    for item in structural:
        if item == _PRODUCT_CODE_FACET and any(
            _facet_covers_product_code_filter(f) for f in merged
        ):
            continue
        _add(item)

    return merged[:_MAX_FACETS]
