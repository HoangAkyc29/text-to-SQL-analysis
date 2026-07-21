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
            "text": "SELECT hidden_value FROM hidden_table",
            "embedding": [0.8, 0.2],
            "status": "promoted",
            "case_id": "c1",
            "scope": "global",
            "analysis_id": "analysis-1",
            "source_trace_id": "trace-1",
            "sql_template": ["SELECT secret_recipe"],
            "links": [
                {"chunk_group": "column", "ref": "amount_bill_header"},
                {"chunk_group": "table", "ref": "db2:transhdr"},
            ],
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
    assert payload["case_studies"]
    case = payload["case_studies"][0]
    assert "sql_template" not in case
    assert "SELECT" not in case["text"]
    assert case["provenance"]["source_trace_id"] == "trace-1"
    assert case["links"] == [
        {"chunk_group": "column", "ref": "amount_bill_header"},
        {"chunk_group": "table", "ref": "db2:transhdr"},
    ]


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
        {
            "text": "vip revenue case",
            "embedding": [1.0, 0.0],
            "status": "promoted",
            "case_id": "c1",
            "scope": "global",
            "links": [{"chunk_group": "table", "ref": "db2:strans"}],
        }
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


def test_case_retrieval_is_promoted_only_and_actor_scoped():
    coll = InMemoryCollection()
    for case_id, status, scope, actor_id in (
        ("allowed", "promoted", "actor", "u1"),
        ("other-user", "promoted", "actor", "u2"),
        ("staged", "staged", "actor", "u1"),
        ("global", "promoted", "global", "owner"),
    ):
        coll.insert_one(
            {
                "case_id": case_id,
                "text": "revenue case",
                "embedding": [1.0, 0.0],
                "status": status,
                "scope": scope,
                "actor_id": actor_id,
            }
        )
    retriever = MongoVectorRetriever(
        _FakeDb({"case_studies": coll}),
        embedder=_StubEmbedder(),
        min_score=0.0,
    )

    chunks = retriever.retrieve("revenue", top_k=10, filters={"actor_id": "u1"})

    assert {chunk.source for chunk in chunks} == {"allowed", "global"}


def test_case_compatibility_and_threshold_rejections_are_audited():
    coll = InMemoryCollection()
    coll.insert_one(
        {
            "case_id": "schema-mismatch",
            "text": "unrelated",
            "embedding": [1.0, 0.0],
            "status": "promoted",
            "scope": "global",
            "schema_version": "v1",
            "links": [{"chunk_group": "table", "ref": "db1:archive"}],
        }
    )
    coll.insert_one(
        {
            "case_id": "low-score",
            "text": "unrelated",
            "embedding": [-1.0, 0.0],
            "status": "promoted",
            "scope": "global",
            "schema_version": "v2",
            "links": [{"chunk_group": "table", "ref": "db2:live"}],
        }
    )
    retriever = MongoVectorRetriever(
        _FakeDb({"case_studies": coll}),
        embedder=_StubEmbedder(),
        min_score=0.5,
    )

    chunks = retriever.retrieve(
        "revenue",
        top_k=10,
        filters={
            "actor_id": "u1",
            "schema_version": "v2",
            "compatible_link_refs": ["db2:live"],
            "compatible_table_refs": ["db2:live"],
        },
    )

    assert chunks == []
    assert retriever.last_retrieval_audit["rejected"] == {
        "schema_version_mismatch": 1,
        "below_score_threshold": 1,
    }
