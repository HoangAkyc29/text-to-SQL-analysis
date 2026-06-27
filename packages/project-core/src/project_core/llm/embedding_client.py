from __future__ import annotations

from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from project_core.config.loader import get_openrouter_api_key, load_models_config
from project_core.domain.errors.codes import LLMProviderError


class EmbeddingClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key or get_openrouter_api_key()
        self.base_url = (base_url or "https://openrouter.ai/api/v1").rstrip("/")
        self.timeout = timeout

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=8))
    def embed(self, texts: list[str], profile_name: str = "openrouter_embed") -> list[list[float]]:
        cfg = load_models_config()
        profile = cfg.profiles.get(profile_name)
        if profile is None:
            raise LLMProviderError(f"Unknown embed profile: {profile_name}")
        payload: dict[str, Any] = {
            "model": profile.model_id,
            "input": texts,
        }
        response = requests.post(
            f"{self.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=self.timeout,
        )
        if not response.ok:
            raise LLMProviderError(
                f"OpenRouter embeddings HTTP {response.status_code}: {response.text[:500]}"
            )
        data = response.json()
        items = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in items]
