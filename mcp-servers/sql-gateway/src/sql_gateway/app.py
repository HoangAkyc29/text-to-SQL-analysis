from __future__ import annotations

from mcp_core.server.lifecycle.base import ServerInfo
from mcp_core.server.lifecycle.fastmcp_server import FastMCPServer
from mcp_core.server.transport import transport_from_env

from sql_gateway.providers import SqlGatewayToolProvider


def build_server() -> FastMCPServer:
    server = FastMCPServer(
        ServerInfo(
            name="sql-gateway",
            instructions="SQL validate/explain/execute readonly gateway for supermarket analytics",
        ),
        transport=transport_from_env(),
    )
    server.add_tool_provider(SqlGatewayToolProvider())
    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
