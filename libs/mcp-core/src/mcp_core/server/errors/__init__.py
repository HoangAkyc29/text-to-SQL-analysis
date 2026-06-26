"""Item 47 - Error handling (domain -> JSON-RPC)."""

from mcp_core.server.errors.base import JsonRpcError, MCPErrorMapper

__all__ = ["JsonRpcError", "MCPErrorMapper"]
