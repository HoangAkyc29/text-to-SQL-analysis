"""Entrypoint for base-mcp-server template."""

from __future__ import annotations

from mcp_core.server.lifecycle.base import ServerInfo
from mcp_core.server.lifecycle.fastmcp_server import FastMCPServer
from mcp_core.server.transport import transport_from_env

from base_mcp_server.providers import BaseToolProvider


def build_server() -> FastMCPServer:
    server = FastMCPServer(
        ServerInfo(
            name="base-mcp",
            instructions="Template MCP server — replace tools in tools_impl.py",
        ),
        transport=transport_from_env(),
    )
    server.add_tool_provider(BaseToolProvider())
    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
