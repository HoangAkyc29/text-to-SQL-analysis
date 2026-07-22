"""Retrieval query / facet builders for schema RAG."""

from __future__ import annotations

from project_core.domain.contracts.brief import AnalysisBrief, TimeRange
from project_core.domain.retrieval.query_builder import (
    build_retrieval_facets,
    build_retrieval_query,
)


def test_weak_llm_facets_still_inject_product_code_structural():
    brief = AnalysisBrief(
        intent="Phân tích quà tặng mã 30323",
        metrics=["quantity"],
        filters={"product_code": ["0030323"], "min_bill_value": 600000},
        time_range=TimeRange(start="2026-07-01", end="2026-07-06", grain="day"),
        retrieval_facets=[
            "Phân tích sản phẩm mã 30323",
            "Chỉ số quantity (số lượng)",
            "Lọc bill có giá trị >= 600000",
            "Xếp hạng top 5 bill",
            "Kết quả xuất excel và bảng",
        ],
    )
    facets = build_retrieval_facets(brief)
    assert "Lọc theo mã hàng / SKU hiển thị trên master sản phẩm" in facets
    assert any("quantity" in f.lower() or "số lượng" in f.lower() for f in facets)
    assert len(facets) <= 8


def test_llm_product_filter_facet_not_duplicated():
    brief = AnalysisBrief(
        intent="gift sku",
        filters={"product_code": "0030344"},
        retrieval_facets=[
            "Lọc theo mã sản phẩm 0030344",
            "Thời gian tháng 7",
        ],
    )
    facets = build_retrieval_facets(brief)
    structural = "Lọc theo mã hàng / SKU hiển thị trên master sản phẩm"
    assert structural not in facets or facets.count(structural) <= 1
    assert "Lọc theo mã sản phẩm 0030344" in facets


def test_structural_fallback_when_no_llm_facets():
    brief = AnalysisBrief(
        intent="VIP",
        filters={"product_code": "123"},
        time_range=TimeRange(start="2026-01-01", end="2026-01-31"),
        metrics=["quantity"],
    )
    facets = build_retrieval_facets(brief)
    assert "Lọc theo mã hàng / SKU hiển thị trên master sản phẩm" in facets
    assert any("thời gian" in f.lower() for f in facets)


def test_retrieval_query_uses_filter_type_tokens_only():
    brief = AnalysisBrief(
        intent="làm tương tự mã 30323",
        filters={"product_code": "30323"},
        metrics=["quantity"],
    )
    q = build_retrieval_query(brief.intent, brief)
    assert "product_code" in q
    assert "30323" in q  # from intent text only
    assert "SKU_DEF" not in q
    assert "BARCODE" not in q
