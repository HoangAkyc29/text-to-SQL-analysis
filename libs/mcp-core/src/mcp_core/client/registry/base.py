"""Item 49 - MCP server registry / Multi-server manager.

Connect to many MCP servers at once, namespace their tools (e.g. ``server_a_``,
``server_b_``) and route a call to the right server. Relates to the agent-side Tool
registry (item 10) and Agent registry (item 26).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import ExitStack
from typing import Any

from mcp_core.client.connector.base import MCPConnector, ServerEndpoint
from mcp_core.client.registry.tool_filter import filter_adapted_tools


class MCPServerRegistry(ABC):
    """Manage connections to multiple MCP servers."""

    def __init__(self) -> None:
        self._endpoints: dict[str, ServerEndpoint] = {}
        self._connectors: dict[str, MCPConnector] = {}
        self._stack: ExitStack | None = None

    def add(self, endpoint: ServerEndpoint) -> None:
        self._endpoints[endpoint.name] = endpoint

    @abstractmethod
    def _make_connector(self, endpoint: ServerEndpoint) -> MCPConnector:
        """Build a connector for ``endpoint`` (concrete impl chooses the class)."""

    def connect_all(self) -> None:
        self._stack = ExitStack()
        for name, endpoint in self._endpoints.items():
            connector = self._make_connector(endpoint)
            self._stack.enter_context(connector)
            self._connectors[name] = connector

    def disconnect_all(self) -> None:
        if self._stack is not None:
            self._stack.close()
            self._stack = None
        self._connectors.clear()

    def connector(self, name: str) -> MCPConnector:
        return self._connectors[name]

    def all_tools(self) -> list[Any]:
        """Gather raw tool handles from every connected server."""
        tools: list[Any] = []
        for connector in self._connectors.values():
            tools.extend(connector.list_tools())
        return tools

    def adapted_tools(self, adapter: Any) -> list[Any]:
        """Gather tools from every server, namespaced per its endpoint prefix.

        ``adapter`` is an :class:`MCPAgentAdapter`; this is the item 49 + item 50
        integration: many servers -> one flat, prefixed tool list for an agent.
        """
        tools: list[Any] = []
        for name, connector in self._connectors.items():
            endpoint = self._endpoints[name]
            prefix = endpoint.prefix
            adapted = adapter.adapt_tools(connector.list_tools(), prefix=prefix)
            tools.extend(filter_adapted_tools(adapted, endpoint))
        return tools

    def connector_for(self, name: str) -> MCPConnector:
        return self._connectors[name]

    def __enter__(self) -> "MCPServerRegistry":
        self.connect_all()
        return self

    def __exit__(self, *exc: object) -> None:
        self.disconnect_all()
