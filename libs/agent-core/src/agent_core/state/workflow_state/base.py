"""Item 17 - Workflow / Orchestration State.

Tracks the progress of a multi-step / multi-agent run: which node is active,
which tasks are done, the accumulated results, and overall status. Consumed by
the Orchestrator (item 25) and the Runtime (item 28).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"  # e.g. human-in-the-loop
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class WorkflowState:
    """Mutable state of a workflow execution."""

    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_node: str | None = None
    completed_nodes: list[str] = field(default_factory=list)
    results: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def mark_done(self, node: str, result: Any) -> None:
        if node not in self.completed_nodes:
            self.completed_nodes.append(node)
        self.results[node] = result
