"""Hybrid schema + case study retrieval."""

from __future__ import annotations

from project_core.domain.retrieval.mongo_vector import HybridMongoRetriever, MongoVectorRetriever
from project_test.helpers.fake_mongo import InMemoryCollection


class _FakeDb:
    def __init__(self, collections: dict):
        self._collections = collections

    def __getitem__(self, name: str):
        return self._collections[name]


class _StubEmbedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0] for _ in texts]


def test_hybrid_retriever_merges_collections(monkeypatch):
    monkeypatch.setattr(
        "project_core.domain.retrieval.mongo_vector.EmbeddingClient",
        lambda: _StubEmbedder(),
    )
    case_coll = InMemoryCollection()
    schema_coll = InMemoryCollection()
    case_coll.insert_one(
        {"text": "vip revenue case", "embedding": [1.0, 0.0], "status": "promoted", "case_id": "c1"}
    )
    schema_coll.insert_one(
        {"text": "table STRANS revenue", "embedding": [0.9, 0.1], "table": "STRANS"}
    )
    db = _FakeDb({"case_studies": case_coll, "schema_chunks": schema_coll})
    retriever = HybridMongoRetriever(db)
    chunks = retriever.retrieve("revenue STRANS", top_k=4)
    assert len(chunks) >= 2
    texts = {c.text for c in chunks}
    assert "vip revenue case" in texts
    assert "table STRANS revenue" in texts


def test_schema_retriever_skips_status_filter(monkeypatch):
    monkeypatch.setattr(
        "project_core.domain.retrieval.mongo_vector.EmbeddingClient",
        lambda: _StubEmbedder(),
    )
    coll = InMemoryCollection()
    coll.insert_one({"text": "schema only", "embedding": [1.0, 0.0], "table": "SKU_DEF"})
    retriever = MongoVectorRetriever(
        _FakeDb({"schema_chunks": coll}), collection_name="schema_chunks", skip_status_filter=True
    )
    chunks = retriever.retrieve("SKU", top_k=1)
    assert len(chunks) == 1
