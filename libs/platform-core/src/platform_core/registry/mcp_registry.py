"""Item 49 concrete - the central MCP server registry.

Single place that knows every MCP server and how to reach it. An agent asks for
the endpoints of the servers it declared in ``platform.yaml`` (by name); the
registry resolves transport (stdio vs HTTP) and applies the prefix. No agent
hardcodes a server command or URL.
"""

from __future__ import annotations

import os

from commons.errors import ConfigError
from commons.logging import get_logger

from mcp_core.client.connector.base import ServerEndpoint

from platform_core.config.schema import MCPServerSpec, PlatformConfig

log = get_logger("platform_core.mcp_registry")


class PlatformMCPRegistry:
    """Resolve MCP ``ServerEndpoint``s from the platform config."""

    def __init__(self, config: PlatformConfig) -> None:
        self._config = config

    def _to_endpoint(self, spec: MCPServerSpec) -> ServerEndpoint:
        url = spec.url
        if spec.url_env and os.getenv(spec.url_env):
            url = os.getenv(spec.url_env)
        if url:
            # Honor the declared remote transport; default to streamable-http.
            remote = spec.transport if spec.transport in ("sse", "streamable-http") else "streamable-http"
            return ServerEndpoint(
                name=spec.name,
                transport=remote,
                url=url,
                prefix=spec.prefix,
                tool_filters=list(spec.tool_filters),
            )
        if not spec.command:
            raise ConfigError(f"MCP server '{spec.name}' has neither url nor stdio command")
        return ServerEndpoint(
            name=spec.name,
            transport="stdio",
            command=spec.command,
            args=list(spec.args),
            env={"MCP_TRANSPORT": "stdio"},
            prefix=spec.prefix,
            tool_filters=list(spec.tool_filters),
        )

    def endpoints_for(self, server_names: list[str]) -> list[ServerEndpoint]:
        """Return endpoints for the named servers (in declared order)."""
        endpoints: list[ServerEndpoint] = []
        for name in server_names:
            if name not in self._config.mcp_servers:
                raise ConfigError(f"Unknown MCP server '{name}'")
            endpoints.append(self._to_endpoint(self._config.mcp_servers[name]))
        return endpoints

    def all_endpoints(self) -> list[ServerEndpoint]:
        return [self._to_endpoint(s) for s in self._config.mcp_servers.values()]
