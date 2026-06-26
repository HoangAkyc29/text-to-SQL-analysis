"""Strands-backed multi-server registry: builds StrandsMCPConnector per endpoint."""

from __future__ import annotations

from mcp_core.client.connector.base import MCPConnector, ServerEndpoint
from mcp_core.client.connector.strands_connector import StrandsMCPConnector
from mcp_core.client.registry.base import MCPServerRegistry


class StrandsMCPServerRegistry(MCPServerRegistry):
    def _make_connector(self, endpoint: ServerEndpoint) -> MCPConnector:
        return StrandsMCPConnector(endpoint)
