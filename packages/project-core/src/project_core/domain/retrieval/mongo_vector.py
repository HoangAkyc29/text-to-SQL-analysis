from __future__ import annotations

from typing import Any

from agent_core.capabilities.retrieval.base import RetrievedChunk, Retriever
from project_core.llm.embedding_client import EmbeddingClient


class MongoVectorRetriever(Retriever):
    def __init__(self, db: Any, *, collection_name: str = "case_studies") -> None:
        from typing import Any as _Any  # noqa: PLC0415

        self.db = db
        self.collection = db[collection_name]
        self.embedder = EmbeddingClient()

    def index(self, documents: list[str], *, metadata: list[dict[str, Any]] | None = None) -> None:
        from typing import Any

        meta = metadata or [{} for _ in documents]
        vectors = self.embedder.embed(documents)
        for text, vec, md in zip(documents, vectors, meta, strict=True):
            self.collection.insert_one({"text": text, "embedding": vec, **md})

    def retrieve(self, query: str, *, top_k: int = 5, filters: dict[str, Any] | None = None) -> list[RetrievedChunk]:
        filters = filters or {}
        query_vec = self.embedder.embed([query])[0]
        status_filter = {"$in": ["promoted", "staged"]}
        mongo_filter: dict[str, Any] = {"status": status_filter}
        if filters.get("actor_id"):
            mongo_filter["$or"] = [{"scope": "global"}, {"actor_id": filters["actor_id"]}]
        docs = list(self.collection.find(mongo_filter).limit(200))
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
                    source=doc.get("case_id", ""),
                    metadata={k: v for k, v in doc.items() if k not in {"embedding", "text"}},
                )
            )
        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[:top_k]


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
