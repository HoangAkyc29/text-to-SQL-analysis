"""Tool name filtering for MCP server endpoints."""

from __future__ import annotations

import fnmatch
from typing import Any

from mcp_core.client.connector.base import ServerEndpoint


def tool_name(value: Any) -> str:
    if isinstance(value, str):
        return value
    return str(getattr(value, "name", value))


def bare_tool_name(prefixed: str, prefix: str | None) -> str:
    if prefix and prefixed.startswith(f"{prefix}_"):
        return prefixed[len(prefix) + 1 :]
    return prefixed


def matches_tool_filter(prefixed: str, bare: str, filters: list[str]) -> bool:
    for pattern in filters:
        if pattern in (prefixed, bare):
            return True
        if fnmatch.fnmatch(prefixed, pattern) or fnmatch.fnmatch(bare, pattern):
            return True
    return False


def filter_adapted_tools(tools: list[Any], endpoint: ServerEndpoint) -> list[Any]:
    if not endpoint.tool_filters:
        return tools
    prefix = endpoint.prefix
    kept: list[Any] = []
    for tool in tools:
        name = tool_name(tool)
        bare = bare_tool_name(name, prefix)
        if matches_tool_filter(name, bare, endpoint.tool_filters):
            kept.append(tool)
    return kept
