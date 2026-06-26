"""Auth middleware wrapping MCP tool handlers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from mcp_core.server.auth.base import AuthContext, Authorizer


def extract_bearer(headers: dict[str, str] | None) -> str | None:
    if not headers:
        return None
    auth = headers.get("Authorization") or headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


def guarded_tool(
    authorizer: Authorizer,
    tool_name: str,
    handler: Callable[..., Any],
    *,
    headers: dict[str, str] | None = None,
) -> Callable[..., Any]:
    """Wrap a tool handler with authenticate + authorize checks."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        token = extract_bearer(headers)
        ctx = authorizer.authenticate(token)
        if not authorizer.authorize(ctx, target=tool_name, action="call"):
            raise PermissionError(f"not authorized to call tool '{tool_name}'")
        return handler(*args, **kwargs)

    wrapper.__name__ = getattr(handler, "__name__", tool_name)
    return wrapper


class AuthMiddleware:
    """Apply auth to a :class:`ToolProvider` before binding to FastMCP."""

    def __init__(self, authorizer: Authorizer) -> None:
        self.authorizer = authorizer

    def wrap_provider(self, provider: Any, *, headers: dict[str, str] | None = None) -> Any:
        from mcp_core.server.providers.tools.base import ToolDefinition, ToolProvider

        class _GuardedProvider(ToolProvider):
            def __init__(self, outer: AuthMiddleware, inner: Any) -> None:
                self._outer = outer
                self._inner = inner

            def list_tools(self) -> list[ToolDefinition]:
                return self._inner.list_tools()

            def bind(self, mcp: Any) -> None:
                for tool in self._inner.list_tools():
                    mcp.tool(name=tool.name, description=tool.description)(
                        guarded_tool(self._outer.authorizer, tool.name, tool.handler, headers=headers)
                    )

        return _GuardedProvider(self, provider)
