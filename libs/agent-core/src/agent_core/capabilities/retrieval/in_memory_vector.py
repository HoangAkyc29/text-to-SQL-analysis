"""In-memory vector retriever (numpy cosine similarity)."""

from __future__ import annotations

from typing import Any

from agent_core.capabilities.retrieval.base import EmbeddingModel, RetrievedChunk, Retriever


class InMemoryVectorRetriever(Retriever):
    def __init__(self, embedding_model: EmbeddingModel) -> None:
        self._embedder = embedding_model
        self._texts: list[str] = []
        self._metadata: list[dict[str, Any]] = []
        self._vectors: list[list[float]] = []

    def index(self, documents: list[str], *, metadata: list[dict[str, Any]] | None = None) -> None:
        meta = metadata or [{} for _ in documents]
        vectors = self._embedder.embed(documents)
        self._texts.extend(documents)
        self._metadata.extend(meta)
        self._vectors.extend(vectors)

    def retrieve(self, query: str, *, top_k: int = 5) -> list[RetrievedChunk]:
        if not self._texts:
            return []
        import numpy as np

        qv = np.array(self._embedder.embed([query])[0])
        scores: list[tuple[float, int]] = []
        for i, vec in enumerate(self._vectors):
            v = np.array(vec)
            denom = np.linalg.norm(qv) * np.linalg.norm(v)
            score = float(np.dot(qv, v) / denom) if denom else 0.0
            scores.append((score, i))
        scores.sort(reverse=True)
        out: list[RetrievedChunk] = []
        for score, idx in scores[:top_k]:
            out.append(
                RetrievedChunk(
                    text=self._texts[idx],
                    score=score,
                    source=str(self._metadata[idx].get("source", "")),
                    metadata=self._metadata[idx],
                )
            )
        return out
