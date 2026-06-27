from __future__ import annotations

from project_core.domain.contracts.workflow import WorkflowState, WorkflowStatus


class CancellationToken:
    def __init__(self) -> None:
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    @property
    def cancelled(self) -> bool:
        return self._cancelled


def mark_cancelled(workflow: WorkflowState) -> None:
    workflow.status = WorkflowStatus.CANCELLED
