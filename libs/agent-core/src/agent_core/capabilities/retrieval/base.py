"""Item 13 - Retriever / Embedding (RAG layer).

Separated from the memory store: embeddings + similarity search over a vector
index.

    embed(texts)      -> vectors
    retrieve(query)   -> ranked chunks
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RetrievedChunk:
    """A scored chunk returned from retrieval."""

    text: str
    score: float
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class EmbeddingModel(ABC):
    """Map text to dense vectors."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class Retriever(ABC):
    """Index documents and retrieve relevant chunks for a query."""

    @abstractmethod
    def index(self, documents: list[str], *, metadata: list[dict[str, Any]] | None = None) -> None: ...

    @abstractmethod
    def retrieve(self, query: str, *, top_k: int = 5) -> list[RetrievedChunk]: ...
