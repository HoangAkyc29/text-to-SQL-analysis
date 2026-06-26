"""Item 43 - Client-callback handler (server -> client).

Primitives where the server calls back into the client:
  - sampling: ask the client's LLM for a completion (uses client Model, item 6)
  - elicitation: ask the user for input (human-in-the-loop, item 29)
  - roots: query the client's filesystem/URI boundaries

These keep the user/client in control.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SamplingRequest:
    messages: list[dict[str, Any]]
    max_tokens: int = 512
    system_prompt: str | None = None


@dataclass(slots=True)
class ElicitationRequest:
    prompt: str
    schema: dict[str, Any] = field(default_factory=dict)


class ClientCallbacks(ABC):
    """Server-initiated requests back to the client."""

    @abstractmethod
    async def sample(self, request: SamplingRequest) -> str:
        """Ask the client's model for a completion."""

    @abstractmethod
    async def elicit(self, request: ElicitationRequest) -> dict[str, Any]:
        """Ask the user (via client) for structured input."""

    async def roots(self) -> list[str]:
        """Return client-exposed root URIs. Default: none."""
        return []
