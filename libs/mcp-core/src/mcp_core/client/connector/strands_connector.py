"""Strands-backed reference implementation of :class:`MCPConnector`.

Builds a ``strands.tools.mcp.MCPClient`` from a :class:`ServerEndpoint`, choosing
stdio, streamable-http, or SSE transport.
"""

from __future__ import annotations

from typing import Any

from commons.logging import get_logger

from mcp_core.client.connector.base import MCPConnector, ServerEndpoint

log = get_logger(__name__)


class StrandsMCPConnector(MCPConnector):
    """Wrap ``strands.tools.mcp.MCPClient`` for one server."""

    def __init__(self, endpoint: ServerEndpoint) -> None:
        super().__init__(endpoint)
        self._client: Any = None

    def _build_client(self) -> Any:
        from strands.tools.mcp import MCPClient

        ep = self.endpoint
        if ep.transport == "stdio":
            from mcp import StdioServerParameters, stdio_client

            if not ep.command:
                raise ValueError(f"stdio endpoint '{ep.name}' requires a command")

            def transport() -> Any:
                return stdio_client(
                    StdioServerParameters(
                        command=ep.command,
                        args=ep.args,
                        env=ep.env or None,
                        cwd=ep.cwd,
                    )
                )

        elif ep.transport in ("streamable-http", "sse"):
            if not ep.url:
                raise ValueError(f"http endpoint '{ep.name}' requires a url")
            if ep.transport == "sse":
                from mcp.client.sse import sse_client

                def transport() -> Any:
                    return sse_client(ep.url, headers=ep.headers or None)
            else:
                from mcp.client.streamable_http import streamablehttp_client

                def transport() -> Any:
                    return streamablehttp_client(ep.url, headers=ep.headers or None)
        else:  # pragma: no cover - guarded by type
            raise ValueError(f"Unsupported transport: {ep.transport}")

        return MCPClient(transport)

    def connect(self) -> None:
        if self._client is None:
            self._client = self._build_client()
        self._client.start()
        log.info("Connected to MCP server '%s' via %s", self.endpoint.name, self.endpoint.transport)

    def disconnect(self) -> None:
        if self._client is not None:
            self._client.stop(None, None, None)

    @property
    def raw_client(self) -> Any:
        if self._client is None:
            raise RuntimeError("connect() must be called first")
        return self._client

    def list_tools(self) -> list[Any]:
        tools: list[Any] = []
        token: str | None = None
        while True:
            page = self.raw_client.list_tools_sync(pagination_token=token)
            tools.extend(page)
            token = getattr(page, "token", None)
            if not token:
                break
        return tools

    def list_resources(self) -> list[Any]:
        try:
            return list(self.raw_client.list_resources_sync())
        except Exception:  # noqa: BLE001 - resources optional
            return []

    def list_prompts(self) -> list[Any]:
        try:
            return list(self.raw_client.list_prompts_sync().prompts)
        except Exception:  # noqa: BLE001 - prompts optional
            return []
