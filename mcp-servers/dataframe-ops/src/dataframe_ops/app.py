from __future__ import annotations

from mcp_core.server.lifecycle.base import ServerInfo
from mcp_core.server.lifecycle.fastmcp_server import FastMCPServer
from mcp_core.server.transport import transport_from_env

from dataframe_ops.providers import DataframeOpsToolProvider


def build_server() -> FastMCPServer:
    server = FastMCPServer(
        ServerInfo(
            name="dataframe-ops",
            instructions="Working-set dataframe transform/inspect ops over disk parquet refs.",
        ),
        transport=transport_from_env(),
    )
    server.add_tool_provider(DataframeOpsToolProvider())
    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
