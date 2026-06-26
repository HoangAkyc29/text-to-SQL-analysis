"""Item 38 - Transport.

Abstracts how a server is reached: locally over stdio, or remotely over HTTP.
Two remote flavours are supported, both standard MCP:

  - Streamable HTTP (the modern default) at ``/mcp``
  - SSE (the legacy HTTP+SSE transport) at ``/sse``

The same server logic runs over any of them by selecting a transport.
``fastmcp_run_kwargs`` maps the transport to ``FastMCP.run`` args, while
``fastmcp_settings`` returns the ``FastMCP(...)`` constructor settings (host/port/
path) so the server actually binds where configured.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class TLSConfig:
    """TLS settings for HTTP/SSE MCP transports."""

    certfile: str | None = None
    keyfile: str | None = None
    ca_certs: str | None = None

    @classmethod
    def from_env(cls) -> "TLSConfig":
        return cls(
            certfile=os.getenv("MCP_TLS_CERT"),
            keyfile=os.getenv("MCP_TLS_KEY"),
            ca_certs=os.getenv("MCP_TLS_CA"),
        )

    def ssl_kwargs(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.certfile and self.keyfile:
            out["ssl_certfile"] = self.certfile
            out["ssl_keyfile"] = self.keyfile
        if self.ca_certs:
            out["ssl_ca_certs"] = self.ca_certs
        return out


class ServerTransport(ABC):
    """Base transport configuration for a server."""

    kind: str = "abstract"

    @abstractmethod
    def fastmcp_run_kwargs(self) -> dict[str, Any]:
        """Return kwargs for ``FastMCP.run`` for this transport."""

    def fastmcp_settings(self) -> dict[str, Any]:
        """Return ``FastMCP(...)`` constructor settings (host/port/path).

        Empty for stdio; HTTP-like transports override to bind host/port/path.
        """
        return {}


class StdioTransport(ServerTransport):
    """Local transport: spawn + talk over stdin/stdout."""

    kind = "stdio"

    def fastmcp_run_kwargs(self) -> dict[str, Any]:
        return {"transport": "stdio"}


class StreamableHttpTransport(ServerTransport):
    """Remote transport: Streamable HTTP (the modern MCP HTTP transport)."""

    kind = "streamable-http"

    def __init__(self, *, host: str = "0.0.0.0", port: int = 8000, path: str = "/mcp", tls: TLSConfig | None = None) -> None:
        self.host = host
        self.port = port
        self.path = path
        self.tls = tls or TLSConfig.from_env()

    def fastmcp_run_kwargs(self) -> dict[str, Any]:
        return {"transport": "streamable-http", **self.tls.ssl_kwargs()}

    def fastmcp_settings(self) -> dict[str, Any]:
        return {"host": self.host, "port": self.port, "streamable_http_path": self.path}


class SseTransport(ServerTransport):
    """Remote transport: HTTP + SSE (the legacy MCP transport, served at /sse)."""

    kind = "sse"

    def __init__(self, *, host: str = "0.0.0.0", port: int = 8000, path: str = "/sse", tls: TLSConfig | None = None) -> None:
        self.host = host
        self.port = port
        self.path = path
        self.tls = tls or TLSConfig.from_env()

    def fastmcp_run_kwargs(self) -> dict[str, Any]:
        return {"transport": "sse", **self.tls.ssl_kwargs()}

    def fastmcp_settings(self) -> dict[str, Any]:
        return {"host": self.host, "port": self.port, "sse_path": self.path}


def transport_from_env() -> ServerTransport:
    """Build a transport from MCP_* environment variables.

    MCP_TRANSPORT = stdio | streamable-http | sse (default stdio)
    MCP_HTTP_HOST, MCP_HTTP_PORT for the bind address (HTTP + SSE).
    MCP_HTTP_PATH (default /mcp) for Streamable HTTP; MCP_SSE_PATH (default /sse) for SSE.
    """
    kind = os.getenv("MCP_TRANSPORT", "stdio").lower()
    host = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_HTTP_PORT", "8000"))
    if kind == "sse":
        return SseTransport(host=host, port=port, path=os.getenv("MCP_SSE_PATH", "/sse"))
    if kind in ("http", "streamable-http"):
        return StreamableHttpTransport(
            host=host, port=port, path=os.getenv("MCP_HTTP_PATH", "/mcp")
        )
    return StdioTransport()
