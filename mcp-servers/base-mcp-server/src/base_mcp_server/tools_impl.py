"""MCP tool handlers — add functions here; BaseToolProvider auto-registers them."""

from __future__ import annotations


def base_ping(message: str = "hello") -> dict:
    """TODO: replace with real MCP tools (feat_*, plot_*, trade_*, …)."""
    return {"status": "todo", "pong": message}
