"""Item 22 - Task decomposition / system-level planner.

Splits a large goal into a graph of subtasks assigned to agents/capabilities.
This is system-level planning (who does what), distinct from intra-agent
reasoning (item 3, how one agent thinks).

    decompose(goal) -> list[Task]
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from agent_core.tasks.task.base import Task


class TaskDecomposer(ABC):
    """Turn a goal into an executable set of tasks with dependencies."""

    @abstractmethod
    def decompose(self, goal: str, *, context: dict[str, Any] | None = None) -> list[Task]:
        """Return tasks (already linked via ``depends_on``)."""

    def validate(self, tasks: list[Task]) -> None:
        """Best-effort cycle / dangling-dependency check."""
        ids = {t.id for t in tasks}
        for t in tasks:
            for dep in t.depends_on:
                if dep not in ids:
                    raise ValueError(f"Task {t.id} depends on unknown task {dep}")
