"""Item 40 - Tool provider (primitive: action).

Tools are model-controlled functions with a JSON schema. This maps to the agent
side's Tool (item 9). A provider groups related tools and binds them to a
FastMCP instance.

    list_tools()           -> [ToolDefinition]
    call_tool(name, args)  -> result
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ToolDefinition:
    """Declarative tool description + handler."""

    name: str
    description: str
    handler: Callable[..., Any]
    input_schema: dict[str, Any] = field(default_factory=dict)


class ToolProvider(ABC):
    """Provide a set of MCP tools and bind them to a server."""

    @abstractmethod
    def list_tools(self) -> list[ToolDefinition]:
        """Return the tools this provider exposes."""

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Invoke a tool by name (used for in-process testing)."""
        for tool in self.list_tools():
            if tool.name == name:
                return tool.handler(**arguments)
        raise KeyError(f"Unknown tool: {name}")

    def bind(self, mcp: Any) -> None:
        """Register every tool on a FastMCP instance."""
        for tool in self.list_tools():
            mcp.tool(name=tool.name, description=tool.description)(tool.handler)
