from __future__ import annotations

from mcp_core.server.lifecycle.base import ServerInfo
from mcp_core.server.lifecycle.fastmcp_server import FastMCPServer
from mcp_core.server.transport import transport_from_env

from data_query.providers import DataQueryToolProvider


def build_server() -> FastMCPServer:
    server = FastMCPServer(
        ServerInfo(
            name="data-query",
            instructions=(
                "Flexible parameterized SQL fetch (query_rows/aggregate_rows/preview/lookup_distinct). "
                "Agents never send raw SQL."
            ),
        ),
        transport=transport_from_env(),
    )
    server.add_tool_provider(DataQueryToolProvider())
    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
