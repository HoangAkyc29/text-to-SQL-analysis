"""Item 6 - Model / LLM provider.

Abstracts the creation of a Strands-compatible model object from a declarative
profile, so the provider (OpenRouter, Bedrock, Ollama, ...) is swappable by
config.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Declarative model profile."""

    provider: str = "openrouter"
    model_id: str
    temperature: float = 0.2
    max_tokens: int | None = None
    supports_vision: bool = False
    params: dict[str, Any] = Field(default_factory=dict)


class ModelProvider(ABC):
    """Create a Strands model instance from a :class:`ModelConfig`."""

    def __init__(self, config: ModelConfig) -> None:
        self.config = config

    @abstractmethod
    def create(self) -> Any:
        """Return a Strands-compatible model object (e.g. an OpenAI-compatible model).

        Implementations import the concrete Strands model class lazily so this
        abstraction stays provider-agnostic.
        """
