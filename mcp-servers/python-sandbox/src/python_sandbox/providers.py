from __future__ import annotations

import inspect

from mcp_core.server.providers.tools.base import ToolDefinition, ToolProvider

from python_sandbox import tools_impl as impl


class SandboxToolProvider(ToolProvider):
    def list_tools(self) -> list[ToolDefinition]:
        tools: list[ToolDefinition] = []
        for name, fn in inspect.getmembers(impl, inspect.isfunction):
            if name.startswith("_"):
                continue
            if getattr(fn, "__module__", None) != impl.__name__:
                continue
            doc = (fn.__doc__ or name).strip().split("\n")[0]
            tools.append(ToolDefinition(name=name, description=doc, handler=fn))
        return tools
