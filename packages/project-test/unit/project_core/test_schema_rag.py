"""Schema RAG retrieval unit tests."""

from __future__ import annotations

from typing import Any

import pytest

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.retrieval.hierarchical_result import HierarchicalRetrievalResult
from project_core.domain.retrieval.mongo_vector import (
    HierarchicalSchemaRetriever,
    _keyword_overlap,
    demote_candidate_tables,
    fuse_facet_scores,
    pick_table_refs,
)
from project_core.domain.retrieval.query_builder import (
    build_retrieval_facets,
    build_retrieval_query,
    sanitize_retrieval_text,
)
from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog

pytestmark = pytest.mark.unit


class _FakeCursor:
    def __init__(self, docs: list[dict[str, Any]]) -> None:
        self._docs = docs

    def limit(self, _n: int) -> list[dict[str, Any]]:
        return list(self._docs)


class _FakeCollection:
    def __init__(self, docs: list[dict[str, Any]]) -> None:
        self.docs = docs

    def find(self, filt: dict[str, Any] | None = None) -> _FakeCursor:
        filt = filt or {}
        out = []
        for d in self.docs:
            if filt.get("chunk_group") and d.get("chunk_group") != filt["chunk_group"]:
                continue
            if "$or" in filt:
                scope_ok = d.get("scope") == "global"
                actor_ok = d.get("actor_id") == next(
                    (c.get("actor_id") for c in filt["$or"] if "actor_id" in c), None
                )
                if not (scope_ok or actor_ok):
                    continue
            if filt.get("status") and d.get("status") not in (filt["status"].get("$in") or []):
                continue
            out.append(d)
        return _FakeCursor(out)


class _FakeDB(dict):
    def __getitem__(self, key: str) -> _FakeCollection:
        return dict.__getitem__(self, key)


class _FakeEmbedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]


def test_schema_retrieve_ignores_actor_id():
    docs = [
        {
            "chunk_group": "column",
            "chunk_id": "sale_line_document_type",
            "semantic_key": "sale_line_document_type",
            "display_names": ["TRANS_CODE"],
            "text": "column sale_line_document_type (TRANS_CODE) on STRANS bill",
            "embedding": [1.0, 0.0, 0.0],
            "tables": [{"ref": "db2:strans", "column": "TRANS_CODE"}],
            "facts": [],
        },
        {
            "chunk_group": "table",
            "chunk_id": "db2:strans",
            "table": "db2:strans",
            "column_names": ["SKU_ID", "TRANS_NUM", "TRANS_CODE"],
            "text": "table db2:strans Columns: SKU_ID, TRANS_NUM, TRANS_CODE",
            "embedding": [0.9, 0.1, 0.0],
            "join_hints": ["Lien ket: TRANS_NUM -> TRANSHDR"],
        },
    ]
    db = _FakeDB(
        {
            "schema_chunks": _FakeCollection(docs),
            "case_studies": _FakeCollection([]),
        }
    )
    retriever = HierarchicalSchemaRetriever(db, embedder=_FakeEmbedder())  # type: ignore[arg-type]
    result = retriever.retrieve_hierarchical(
        "bill TRANS_CODE sales",
        top_k=5,
        filters={"actor_id": "user-1", "include_negative": True},
    )
    assert result.columns, "schema columns must return without scope/actor_id on docs"
    assert any("strans" in t for t in result.candidate_tables)


def test_hybrid_keyword_boosts_display_name():
    doc = {
        "text": "unrelated",
        "semantic_key": "sale_line_document_type",
        "display_names": ["TRANS_CODE"],
        "column_names": [],
    }
    score = _keyword_overlap("TRANS_CODE bill document", doc)
    assert score > 0.0


def test_build_retrieval_query_keeps_intent_digits_adds_filter_types():
    brief = AnalysisBrief(
        intent="gift bill quantity product 0030344",
        filters={"product_code": ["0030344", "0030348"], "min_bill_value": 600000},
        time_range={"start": "2026-07-01", "end": "2026-07-06"},
        metrics=["qty"],
    )
    q = build_retrieval_query(brief.intent, brief)
    assert "0030344" in q
    assert "product_code" in q
    assert "min_bill_value" in q
    assert "date_range" in q
    # Filter values are type tokens only — raw amount not dumped from filters.
    assert "600000" not in q


def test_sanitize_keeps_digits_and_agent_facets():
    assert "0030344" in sanitize_retrieval_text("mã 0030344 và 600000")
    assert "600000" in sanitize_retrieval_text("mã 0030344 và 600000")
    brief = AnalysisBrief(
        intent="x",
        retrieval_facets=["Lọc theo mã sản phẩm 0030344, 0030348"],
        filters={"product_code": ["0030344"], "min_bill_value": 600000},
        time_range={"start": "2026-07-01", "end": "2026-07-06"},
        metrics=["quantity"],
    )
    facets = build_retrieval_facets(brief)
    assert "Lọc theo mã sản phẩm 0030344, 0030348" in facets
    # LLM already covered product-code filter; structural duplicate should not replace it
    assert len(facets) <= 8


def test_fuse_facet_scores_prefers_strong_match():
    weak_even = fuse_facet_scores([0.2, 0.2, 0.2])
    strong_one = fuse_facet_scores([0.9, 0.05, 0.05])
    assert strong_one > weak_even
    assert fuse_facet_scores([-0.1, -0.2]) == max([-0.1, -0.2])


def test_pick_and_demote_noise_tables():
    tables = [
        {"ref": "db2:strans_tmp"},
        {"ref": "db2:webrpt_sales_sku_daily"},
        {"ref": "db2:strans"},
        {"ref": "db2:suspend"},
        {"ref": "db1:strans"},
    ]
    picked = pick_table_refs(tables, max_n=2)
    assert "db2:strans" in picked
    assert "db2:strans_tmp" not in picked
    assert "db2:webrpt_sales_sku_daily" not in picked
    demoted = demote_candidate_tables(
        {"db2:strans", "db2:strans_tmp", "db2:webrpt_sales_sku_daily", "db1:transhdr_arc", "db2:transhdr"},
        query_blob="quantity bill header",
    )
    assert "db2:strans" in demoted
    assert "db2:transhdr" in demoted
    assert "db2:strans_tmp" not in demoted
    assert "db2:webrpt_sales_sku_daily" not in demoted
    assert "db1:transhdr_arc" not in demoted


def test_hierarchical_budget_col_tbl():
    import math

    top_k = 20
    col_k = max(2, top_k)
    tbl_k = max(2, math.ceil(col_k / 2))
    assert col_k == 20
    assert tbl_k == 10


def test_empty_hierarchical_is_miss():
    assert HierarchicalRetrievalResult.is_empty_payload({})
    assert HierarchicalRetrievalResult.is_empty_payload(
        {"phase": "hierarchical", "columns": [], "tables": [], "case_studies": []}
    )
    assert not HierarchicalRetrievalResult.is_empty_payload(
        {"phase": "hierarchical", "columns": [{"semantic_key": "x"}], "tables": []}
    )


def test_table_catalog_key_resolves_db2_strans():
    catalog = SchemaCatalog.from_dictionary_dir()
    meta = catalog.table("db2:strans")
    assert meta is not None
    col_names = [c.name for c in meta.columns]
    assert "SKU_ID" in col_names
    assert "TRANS_NUM" in col_names
    assert catalog.table("strans") is None


def test_embed_text_includes_physical_and_keywords():
    col_catalog = ColumnSemanticCatalog.from_columns_dir()
    # Any key with tables+display_names
    keys = col_catalog.semantic_keys()
    assert keys
    sample = keys[0]
    text = col_catalog.embed_text(sample)
    assert "column " in text
    assert "Keywords:" in text or "Physical:" in text or "Tables:" in text


def test_table_embed_includes_columns():
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[4]
    sys.path.insert(0, str(root))
    from scripts.index_rag_dictionary import _table_embed_text

    catalog = SchemaCatalog.from_dictionary_dir()
    col_catalog = ColumnSemanticCatalog.from_columns_dir()
    text = _table_embed_text(catalog, col_catalog, "db2:strans", "sale lines")
    assert "Columns:" in text
    assert "TRANS_NUM" in text
    assert "SKU_ID" in text
    broken = _table_embed_text(catalog, col_catalog, "strans", "sale lines")
    assert "TRANS_NUM" not in broken
