"""OpenAI-compatible embedding model."""

from __future__ import annotations

import hashlib
import os


class OpenAIEmbeddingModel:
    """Embed via OpenAI / OpenRouter API, with deterministic fallback."""

    def __init__(self, *, model: str = "text-embedding-3-small", dimensions: int = 64) -> None:
        self.model = model
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        if api_key:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=api_key, base_url=base_url)
                resp = client.embeddings.create(model=self.model, input=texts)
                return [list(d.embedding) for d in resp.data]
            except Exception:
                pass
        return [_hash_embed(t, self.dimensions) for t in texts]


def _hash_embed(text: str, dim: int) -> list[float]:
    """Deterministic local fallback when no API key."""
    out = []
    for i in range(dim):
        h = hashlib.sha256(f"{text}:{i}".encode()).digest()
        out.append((h[0] / 255.0) * 2 - 1)
    return out
