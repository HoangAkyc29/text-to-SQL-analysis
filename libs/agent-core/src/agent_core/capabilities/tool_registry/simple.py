"""Concrete tool registry (item 10) for native AbstractTools.

For MCP-sourced tools, the client-side gathering lives in
``mcp_core.client.registry`` (which namespaces remote tools via the adapter).
This registry is the in-process counterpart for native tools.
"""

from __future__ import annotations

from agent_core.capabilities.tool_registry.base import ToolRegistry


class SimpleToolRegistry(ToolRegistry):
    """A registry you populate manually; ``discover`` is a no-op."""

    def discover(self) -> None:
        return None
