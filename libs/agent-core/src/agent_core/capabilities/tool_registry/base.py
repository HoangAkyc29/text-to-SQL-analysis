"""Item 10 - Tool registry / MCP router.

Register tools (native or MCP-adapted), discover them, and select the relevant
subset for a task.

    register(tool)        -> add a tool
    select(task)          -> choose tools for a task
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from agent_core.capabilities.tools.base import AbstractTool, ToolSpec


class ToolSelector(ABC):
    """Choose a subset of tools relevant to a task description."""

    @abstractmethod
    def select(self, task: str, candidates: list[AbstractTool]) -> list[AbstractTool]: ...


class ToolRegistry(ABC):
    """Hold and expose tools; supports namespacing for multi-server setups."""

    def __init__(self, selector: ToolSelector | None = None) -> None:
        self._tools: dict[str, AbstractTool] = {}
        self._selector = selector

    def register(self, tool: AbstractTool, *, namespace: str | None = None) -> None:
        name = tool.spec.name if namespace is None else f"{namespace}_{tool.spec.name}"
        self._tools[name] = tool

    def get(self, name: str) -> AbstractTool:
        return self._tools[name]

    def list_specs(self) -> list[ToolSpec]:
        return [t.spec for t in self._tools.values()]

    def all(self) -> list[AbstractTool]:
        return list(self._tools.values())

    def select(self, task: str) -> list[AbstractTool]:
        if self._selector is None:
            return self.all()
        return self._selector.select(task, self.all())

    @abstractmethod
    def discover(self) -> None:
        """Populate the registry from its sources (plugins, MCP servers, ...)."""
