"""ChromaDB retriever (optional extra)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_core.capabilities.retrieval.base import RetrievedChunk, Retriever


class ChromaRetriever(Retriever):
    def __init__(self, *, persist_dir: Path, collection: str = "agent_docs") -> None:
        import chromadb

        persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(persist_dir))
        self._collection = self._client.get_or_create_collection(collection)

    def index(self, documents: list[str], *, metadata: list[dict[str, Any]] | None = None) -> None:
        meta = metadata or [{} for _ in documents]
        ids = [f"doc-{i}-{hash(d)}" for i, d in enumerate(documents)]
        self._collection.add(documents=documents, metadatas=meta, ids=ids)

    def retrieve(self, query: str, *, top_k: int = 5) -> list[RetrievedChunk]:
        result = self._collection.query(query_texts=[query], n_results=top_k)
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        dists = result.get("distances", [[]])[0]
        out: list[RetrievedChunk] = []
        for text, meta, dist in zip(docs, metas, dists):
            score = 1.0 / (1.0 + float(dist)) if dist is not None else 0.0
            out.append(RetrievedChunk(text=text, score=score, metadata=meta or {}))
        return out
