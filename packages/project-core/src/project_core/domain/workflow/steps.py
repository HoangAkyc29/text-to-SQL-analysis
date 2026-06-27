from __future__ import annotations

from project_core.domain.contracts.workflow import WorkflowStep, WorkflowStepType


def summarize_steps(steps: list[WorkflowStep]) -> list[str]:
    return [f"{s.step_type.value}:{s.summary}" for s in steps]


def has_step_type(steps: list[WorkflowStep], step_type: WorkflowStepType) -> bool:
    return any(s.step_type == step_type for s in steps)
