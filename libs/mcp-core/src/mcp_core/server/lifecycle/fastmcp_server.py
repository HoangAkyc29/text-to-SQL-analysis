"""FastMCP-backed reference implementation of :class:`AbstractMCPServer`.

Concrete servers create one of these, add their providers, and call ``run()``.
Transport is chosen from the :class:`ServerTransport` (stdio or streamable-http).
"""

from __future__ import annotations

from typing import Any

from commons.logging import get_logger

from mcp_core.server.lifecycle.base import AbstractMCPServer, ServerInfo
from mcp_core.server.transport.base import ServerTransport, StdioTransport

log = get_logger(__name__)


class FastMCPServer(AbstractMCPServer):
    """Wraps ``mcp.server.fastmcp.FastMCP``."""

    def __init__(
        self,
        info: ServerInfo,
        *,
        transport: ServerTransport | None = None,
        authorizer: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(info, transport=transport or StdioTransport(), **kwargs)
        self._mcp: Any = None
        self._authorizer = authorizer

    def initialize(self) -> None:
        from mcp.server.fastmcp import FastMCP

        # Pass the transport's host/port/path so HTTP + SSE actually bind where
        # configured (FastMCP otherwise defaults to 127.0.0.1:8000 and ignores
        # the MCP_HTTP_* env vars, which use a different prefix).
        settings = self.transport.fastmcp_settings() if self.transport else {}
        self._mcp = FastMCP(
            self.info.name, instructions=self.info.instructions or None, **settings
        )
        for provider in self._tool_providers:
            if self._authorizer is not None:
                from mcp_core.server.auth.middleware import AuthMiddleware

                provider = AuthMiddleware(self._authorizer).wrap_provider(provider)
            provider.bind(self._mcp)
        for provider in self._resource_providers:
            provider.bind(self._mcp)
        for provider in self._prompt_providers:
            provider.bind(self._mcp)
        log.info(
            "Initialized MCP server '%s' (tool_providers=%d resource_providers=%d prompt_providers=%d)",
            self.info.name,
            len(self._tool_providers),
            len(self._resource_providers),
            len(self._prompt_providers),
        )

    def serve(self) -> None:
        if self._mcp is None:
            raise RuntimeError("serve() called before initialize()")
        assert self.transport is not None
        run_kwargs = self.transport.fastmcp_run_kwargs()
        log.info("Serving '%s' over %s", self.info.name, self.transport.kind)
        self._mcp.run(**run_kwargs)

    def shutdown(self) -> None:
        log.info("Shutting down MCP server '%s'", self.info.name)
        self._mcp = None

    @property
    def mcp(self) -> Any:
        """Expose the underlying FastMCP (for advanced registration)."""
        if self._mcp is None:
            raise RuntimeError("Server not initialized")
        return self._mcp
