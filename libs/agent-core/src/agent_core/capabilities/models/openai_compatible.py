"""Reference ModelProvider for OpenAI-compatible endpoints (e.g. OpenRouter).

Concrete implementation of item 6. Reads credentials from the environment and
builds a Strands ``OpenAIModel``. Kept here (next to ``base.py``) as a reusable
default so every agent does not re-implement it.
"""

from __future__ import annotations

import os
from typing import Any

from agent_core.capabilities.models.base import ModelConfig, ModelProvider


class OpenAICompatibleProvider(ModelProvider):
    """Build a Strands OpenAI-compatible model from a :class:`ModelConfig`."""

    def __init__(self, config: ModelConfig | None = None) -> None:
        super().__init__(
            config
            or ModelConfig(
                provider="openrouter",
                model_id=os.getenv("DEFAULT_MODEL_ID", "openai/gpt-4o-mini"),
            )
        )

    def create(self) -> Any:
        from strands.models.openai import OpenAIModel

        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        return OpenAIModel(
            client_args={"api_key": api_key, "base_url": base_url},
            model_id=self.config.model_id,
            params={"temperature": self.config.temperature, **self.config.params},
        )
