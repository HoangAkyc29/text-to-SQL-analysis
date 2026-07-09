"""Hybrid schema + case study retrieval."""

from __future__ import annotations

from project_core.domain.retrieval.mongo_vector import HierarchicalSchemaRetriever, MongoVectorRetriever
from project_test.helpers.fake_mongo import InMemoryCollection


class _FakeDb:
    def __init__(self, collections: dict):
        self._collections = collections

    def __getitem__(self, name: str):
        return self._collections[name]


class _StubEmbedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        out = []
        for t in texts:
            if "column" in t.lower() or "amount" in t.lower():
                out.append([1.0, 0.0])
            elif "table" in t.lower() or "strans" in t.lower():
                out.append([0.9, 0.1])
            else:
                out.append([0.5, 0.5])
        return out


def test_hierarchical_retriever_column_then_table(monkeypatch):
    monkeypatch.setattr(
        "project_core.domain.retrieval.mongo_vector.EmbeddingClient",
        lambda: _StubEmbedder(),
    )
    case_coll = InMemoryCollection()
    schema_coll = InMemoryCollection()
    case_coll.insert_one(
        {
            "text": "gift bill case",
            "embedding": [0.8, 0.2],
            "status": "promoted",
            "case_id": "c1",
            "links": [{"chunk_group": "column", "ref": "amount_bill_header"}],
        }
    )
    schema_coll.insert_one(
        {
            "chunk_group": "column",
            "chunk_id": "amount_bill_header",
            "semantic_key": "amount_bill_header",
            "display_names": ["AMOUNT"],
            "kind": "measure",
            "tables": [{"ref": "db2:transhdr", "column": "AMOUNT"}],
            "facts": ["min bill header"],
            "text": "column amount_bill_header",
            "embedding": [1.0, 0.0],
        }
    )
    schema_coll.insert_one(
        {
            "chunk_group": "table",
            "chunk_id": "db2:strans",
            "table": "db2:strans",
            "text": "table db2:strans line items",
            "embedding": [0.9, 0.1],
            "join_hints": ["TRANSHDR via TRANS_NUM"],
        }
    )
    db = _FakeDb({"case_studies": case_coll, "schema_chunks": schema_coll})
    retriever = HierarchicalSchemaRetriever(db)
    result = retriever.retrieve_hierarchical("bill amount gift STRANS", top_k=5)
    payload = result.to_payload()
    assert payload["phase"] == "hierarchical" or "columns" in payload
    assert len(payload["columns"]) >= 1
    assert "db2:transhdr" in payload["candidate_tables"] or len(payload["tables"]) >= 1


def test_schema_retriever_filters_chunk_group(monkeypatch):
    monkeypatch.setattr(
        "project_core.domain.retrieval.mongo_vector.EmbeddingClient",
        lambda: _StubEmbedder(),
    )
    coll = InMemoryCollection()
    coll.insert_one(
        {"chunk_group": "column", "text": "column only", "embedding": [1.0, 0.0], "semantic_key": "x"}
    )
    coll.insert_one({"chunk_group": "table", "text": "table only", "embedding": [0.5, 0.5], "table": "T"})
    retriever = MongoVectorRetriever(
        _FakeDb({"schema_chunks": coll}), collection_name="schema_chunks", skip_status_filter=True
    )
    chunks = retriever.retrieve("test", top_k=5, filters={"chunk_group": "column"})
    assert all(c.metadata.get("chunk_group") == "column" for c in chunks)


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
        {
            "chunk_group": "table",
            "text": "table STRANS revenue",
            "embedding": [0.9, 0.1],
            "table": "STRANS",
            "chunk_id": "db2:strans",
        }
    )
    db = _FakeDb({"case_studies": case_coll, "schema_chunks": schema_coll})
    retriever = HierarchicalSchemaRetriever(db)
    chunks = retriever.retrieve("revenue STRANS", top_k=4)
    assert len(chunks) >= 2
