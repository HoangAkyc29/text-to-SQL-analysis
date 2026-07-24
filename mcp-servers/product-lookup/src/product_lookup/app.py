from __future__ import annotations

from mcp_core.server.lifecycle.base import ServerInfo
from mcp_core.server.lifecycle.fastmcp_server import FastMCPServer
from mcp_core.server.transport import transport_from_env

from product_lookup.providers import ProductLookupToolProvider


def build_server() -> FastMCPServer:
    server = FastMCPServer(
        ServerInfo(
            name="product-lookup",
            instructions="Resolve supermarket product codes to SKU_ID via parameterized lookup.",
        ),
        transport=transport_from_env(),
    )
    server.add_tool_provider(ProductLookupToolProvider())
    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
