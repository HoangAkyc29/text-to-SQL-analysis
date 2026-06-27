from __future__ import annotations

from project_core.config.loader import load_project_config
from project_core.domain.contracts.clarification import ClarificationRequest
from project_core.domain.contracts.workflow import WorkflowState


def enforce_clarify_source(request: ClarificationRequest) -> None:
    if request.source_agent != "II":
        raise ValueError("Only Agent II may emit ClarificationRequest")


def can_emit_clarify(workflow: WorkflowState) -> bool:
    cfg = load_project_config()
    return workflow.clarify_round < cfg.pipeline.max_clarify_rounds
