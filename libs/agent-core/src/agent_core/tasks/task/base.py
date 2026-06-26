"""Item 21 - Task / Goal.

A unit of work as a first-class object: input, expected output, dependencies,
and an assignee. Tasks form the graph that decomposition (item 22) produces and
orchestration (item 25) executes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class TaskStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(slots=True)
class Task:
    """A first-class unit of work."""

    goal: str
    id: str = field(default_factory=lambda: str(uuid4()))
    inputs: dict[str, Any] = field(default_factory=dict)
    expected_output: str = ""
    depends_on: list[str] = field(default_factory=list)
    assignee: str | None = None  # agent name / capability
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_ready(self, completed: set[str]) -> bool:
        """A task is ready when all its dependencies are completed."""
        return all(dep in completed for dep in self.depends_on)
