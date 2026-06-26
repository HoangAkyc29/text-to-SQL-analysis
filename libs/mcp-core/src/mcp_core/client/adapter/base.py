"""Item 50 - MCP <-> Agent adapter (bridge).

The most important seam: map MCP primitives onto the agent's internal
abstractions so the agent does not care whether a capability is local or remote.

  - MCP tool      -> agent_core Tool        (item 9)
  - MCP resource  -> agent_core Retriever/Memory source (items 12/13)
  - MCP prompt    -> agent_core PromptTemplate (item 7)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MCPAgentAdapter(ABC):
    """Translate remote MCP primitives into agent-side abstractions."""

    @abstractmethod
    def adapt_tools(self, raw_tools: list[Any], *, prefix: str | None = None) -> list[Any]:
        """Return Strands-/agent-compatible tools (optionally name-prefixed)."""

    def adapt_resources(self, raw_resources: list[Any]) -> list[Any]:
        """Map resources to retrieval/memory sources. Default: passthrough."""
        return list(raw_resources)

    def adapt_prompts(self, raw_prompts: list[Any]) -> list[Any]:
        """Map prompts to PromptTemplates. Default: passthrough."""
        return list(raw_prompts)
