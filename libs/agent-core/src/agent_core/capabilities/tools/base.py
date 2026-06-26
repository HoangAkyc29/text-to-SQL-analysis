"""Item 9 - Tool / Action.

The internal, framework-neutral representation of a callable capability. MCP
tools are mapped onto this via the MCP<->Agent adapter (item 50), so the agent
never needs to know whether a tool is native or remote.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ToolSpec:
    """JSON-schema-style description the model uses to pick/fill a tool."""

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ToolResult:
    """Normalised tool output."""

    ok: bool
    content: Any = None
    error: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


class AbstractTool(ABC):
    """A callable capability with a declarative spec."""

    @property
    @abstractmethod
    def spec(self) -> ToolSpec: ...

    @abstractmethod
    def call(self, **kwargs: Any) -> ToolResult:
        """Execute the tool synchronously."""

    async def acall(self, **kwargs: Any) -> ToolResult:
        """Async variant; defaults to the sync implementation."""
        return self.call(**kwargs)

    def to_strands_tool(self) -> Any:
        """Adapt this tool to a Strands-compatible tool object.

        Override in concrete tools / adapters. Kept abstract-friendly: the base
        raises so implementers are reminded to provide the binding.
        """
        raise NotImplementedError("to_strands_tool must be implemented by the concrete tool/adapter")
