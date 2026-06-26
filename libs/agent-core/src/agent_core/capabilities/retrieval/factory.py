"""Factory for retrieval / RAG backends."""

from __future__ import annotations

from pathlib import Path

from commons.errors import ConfigError

from agent_core.capabilities.retrieval.base import Retriever
from agent_core.infra.backends.config import RetrievalBackendConfig


def build_retriever(
    config: RetrievalBackendConfig,
    *,
    base_dir: Path | None = None,
) -> Retriever | None:
    backend = config.backend.lower()
    if backend in ("none", ""):
        return None
    if backend == "in_memory_vector":
        try:
            from agent_core.capabilities.retrieval.in_memory_vector import InMemoryVectorRetriever
            from agent_core.capabilities.retrieval.openai_embeddings import OpenAIEmbeddingModel
        except ImportError as exc:
            raise ConfigError(
                "in_memory_vector requires agent-core[rag]",
                backend=backend,
            ) from exc
        embedder = OpenAIEmbeddingModel() if config.embedding == "openai" else OpenAIEmbeddingModel()
        return InMemoryVectorRetriever(embedder)
    if backend == "chroma":
        persist = Path(config.persist_dir)
        if base_dir and not persist.is_absolute():
            persist = base_dir / persist
        try:
            from agent_core.capabilities.retrieval.chroma_retriever import ChromaRetriever
        except ImportError as exc:
            raise ConfigError(
                "chroma retriever requires agent-core[chroma]",
                backend=backend,
            ) from exc
        return ChromaRetriever(persist_dir=persist)
    raise ConfigError(f"Unknown retrieval backend: {config.backend}", backend=config.backend)
