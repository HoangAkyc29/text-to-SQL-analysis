"""Strands implementation of the MCP <-> Agent adapter.

Wraps each remote MCP tool in a prefixed Strands tool so multiple servers can be
mounted on one agent without name clashes (e.g. ``billing_``, ``search_``).
"""

from __future__ import annotations

from typing import Any

from commons.logging import get_logger

from mcp_core.client.adapter.base import MCPAgentAdapter

log = get_logger(__name__)


class StrandsMCPAgentAdapter(MCPAgentAdapter):
    """Adapt ``strands.tools.mcp`` tool handles for an agent."""

    def adapt_tools(self, raw_tools: list[Any], *, prefix: str | None = None) -> list[Any]:
        if not prefix:
            return list(raw_tools)
        return [self._prefixed(tool, prefix) for tool in raw_tools]

    @staticmethod
    def _prefixed(tool: Any, prefix: str) -> Any:
        """Return a tool whose advertised name is ``{prefix}_{name}``.

        Strands' ``MCPAgentTool`` exposes the tool spec via ``tool_name`` /
        ``tool_spec``. We subclass lazily to avoid importing strands at module
        import time so the abstraction stays import-light.
        """
        from strands.tools.mcp import MCPAgentTool

        class _PrefixedTool(MCPAgentTool):  # type: ignore[misc]
            def __init__(self, inner: Any) -> None:
                super().__init__(inner.mcp_tool, inner.mcp_client)
                self._prefix = prefix
                self._orig = inner.mcp_tool.name

            @property
            def tool_name(self) -> str:
                return f"{self._prefix}_{self._orig}"

            @property
            def tool_spec(self) -> Any:
                spec = super().tool_spec
                return {**spec, "name": f"{self._prefix}_{self._orig}"}

        return _PrefixedTool(tool)
