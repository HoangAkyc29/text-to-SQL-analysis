from __future__ import annotations

from mcp_core.server.lifecycle.base import ServerInfo
from mcp_core.server.lifecycle.fastmcp_server import FastMCPServer
from mcp_core.server.transport import transport_from_env

from deliverables.providers import DeliverablesToolProvider


def build_server() -> FastMCPServer:
    server = FastMCPServer(
        ServerInfo(
            name="deliverables",
            instructions="Export Excel/CSV, plot charts, inspect and validate deliverables.",
        ),
        transport=transport_from_env(),
    )
    server.add_tool_provider(DeliverablesToolProvider())
    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
