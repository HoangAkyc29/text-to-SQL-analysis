from __future__ import annotations

from mcp_core.server.lifecycle.base import ServerInfo
from mcp_core.server.lifecycle.fastmcp_server import FastMCPServer
from mcp_core.server.transport import transport_from_env

from python_sandbox.providers import SandboxToolProvider


def build_server() -> FastMCPServer:
    server = FastMCPServer(
        ServerInfo(
            name="python-sandbox",
            instructions="Pandas/plot/excel sandbox for Agent IV analytics",
        ),
        transport=transport_from_env(),
    )
    server.add_tool_provider(SandboxToolProvider())
    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
