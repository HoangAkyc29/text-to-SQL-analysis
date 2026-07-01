from __future__ import annotations

import inspect
from functools import partial

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
        tools.extend(self._recipe_tools())
        return tools

    def _recipe_tools(self) -> list[ToolDefinition]:
        out: list[ToolDefinition] = []
        try:
            from project_core.domain.analysis.recipe_runtime import get_registry

            reg = get_registry()
            if not reg:
                return out
            for desc in reg.list_mcp_tool_descriptors():
                tool_id = str(desc["tool_id"])
                name = str(desc["name"])
                handler = partial(impl.run_recipe_tool, tool_id)
                handler.__name__ = name  # type: ignore[attr-defined]
                out.append(
                    ToolDefinition(
                        name=name,
                        description=str(desc.get("description") or f"Promoted recipe {tool_id}"),
                        handler=handler,
                    )
                )
        except Exception:
            return out
        return out
