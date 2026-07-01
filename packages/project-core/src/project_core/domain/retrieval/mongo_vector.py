from __future__ import annotations

from typing import Any

from agent_core.capabilities.retrieval.base import RetrievedChunk, Retriever
from project_core.llm.embedding_client import EmbeddingClient


class MongoVectorRetriever(Retriever):
    def __init__(
        self,
        db: Any,
        *,
        collection_name: str = "case_studies",
        skip_status_filter: bool = False,
    ) -> None:
        from typing import Any as _Any  # noqa: PLC0415

        self.db = db
        self.collection = db[collection_name]
        self.embedder = EmbeddingClient()
        self.skip_status_filter = skip_status_filter

    def index(self, documents: list[str], *, metadata: list[dict[str, Any]] | None = None) -> None:
        from typing import Any

        meta = metadata or [{} for _ in documents]
        vectors = self.embedder.embed(documents)
        for text, vec, md in zip(documents, vectors, meta, strict=True):
            self.collection.insert_one({"text": text, "embedding": vec, **md})

    def retrieve(self, query: str, *, top_k: int = 5, filters: dict[str, Any] | None = None) -> list[RetrievedChunk]:
        filters = filters or {}
        query_vec = self.embedder.embed([query])[0]
        mongo_filter: dict[str, Any] = {}
        if not self.skip_status_filter:
            mongo_filter["status"] = {"$in": ["promoted", "staged"]}
        if filters.get("actor_id"):
            mongo_filter["$or"] = [{"scope": "global"}, {"actor_id": filters["actor_id"]}]
        cursor = self.collection.find(mongo_filter)
        if hasattr(cursor, "limit"):
            docs = list(cursor.limit(200))
        else:
            docs = list(cursor)[:200]
        scored: list[RetrievedChunk] = []
        for doc in docs:
            emb = doc.get("embedding") or []
            score = _cosine(query_vec, emb) if emb else 0.0
            if filters.get("include_negative") and doc.get("status") == "demoted":
                continue
            scored.append(
                RetrievedChunk(
                    text=doc.get("text", ""),
                    score=score,
                    source=doc.get("case_id") or doc.get("table", ""),
                    metadata={k: v for k, v in doc.items() if k not in {"embedding", "text"}},
                )
            )
        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[:top_k]


class HybridMongoRetriever(Retriever):
    """Merge case study RAG with schema chunk RAG for Agent II context."""

    def __init__(self, db: Any) -> None:
        self.case_retriever = MongoVectorRetriever(db, collection_name="case_studies")
        self.schema_retriever = MongoVectorRetriever(
            db, collection_name="schema_chunks", skip_status_filter=True
        )

    def index(self, documents: list[str], *, metadata: list[dict[str, Any]] | None = None) -> None:
        self.case_retriever.index(documents, metadata=metadata)

    def retrieve(self, query: str, *, top_k: int = 5, filters: dict[str, Any] | None = None) -> list[RetrievedChunk]:
        half = max(1, top_k // 2)
        case_chunks = self.case_retriever.retrieve(query, top_k=half, filters=filters)
        schema_chunks = self.schema_retriever.retrieve(query, top_k=top_k - half, filters=filters)
        merged = case_chunks + schema_chunks
        merged.sort(key=lambda c: c.score, reverse=True)
        return merged[:top_k]


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
