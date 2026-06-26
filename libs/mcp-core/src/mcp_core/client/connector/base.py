"""Item 48 - MCP Client / Connector.

Connect to one MCP server, discover its primitives, and proxy remote
tools/resources/prompts as local handles. A Strands-backed reference impl uses
``strands.tools.mcp.MCPClient`` with stdio or streamable-http transport.

    connect()        -> open the session
    discover()       -> list tools/resources/prompts
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(slots=True)
class ServerEndpoint:
    """How to reach a single MCP server."""

    name: str
    transport: Literal["stdio", "streamable-http", "sse"] = "stdio"
    # stdio
    command: str | None = None
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    cwd: str | None = None
    # http
    url: str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    # naming
    prefix: str | None = None
    tool_filters: list[str] = field(default_factory=list)


class MCPConnector(ABC):
    """A connection to a single MCP server."""

    def __init__(self, endpoint: ServerEndpoint) -> None:
        self.endpoint = endpoint

    @abstractmethod
    def connect(self) -> None:
        """Open the session (context-managed by concrete impls)."""

    @abstractmethod
    def disconnect(self) -> None:
        """Close the session."""

    @abstractmethod
    def list_tools(self) -> list[Any]:
        """Return remote tool handles (framework-native, e.g. Strands tools)."""

    @abstractmethod
    def list_resources(self) -> list[Any]:
        """Return remote resource descriptors."""

    @abstractmethod
    def list_prompts(self) -> list[Any]:
        """Return remote prompt descriptors."""

    def __enter__(self) -> "MCPConnector":
        self.connect()
        return self

    def __exit__(self, *exc: object) -> None:
        self.disconnect()
