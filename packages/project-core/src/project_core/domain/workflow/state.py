from __future__ import annotations

from datetime import datetime

from project_core.domain.time import utc_now
from uuid import uuid4

from project_core.domain.contracts.workflow import WorkflowState, WorkflowStatus


def new_workflow(session_id: str, actor_id: str) -> WorkflowState:
    return WorkflowState(session_id=session_id, actor_id=actor_id)


def touch_workflow(workflow: WorkflowState) -> None:
    workflow.updated_at = utc_now()


def suspend_for_clarification(workflow: WorkflowState, trace_id: str) -> None:
    workflow.status = WorkflowStatus.AWAITING_CLARIFICATION
    workflow.suspended_trace_id = trace_id
    touch_workflow(workflow)


def resume_after_clarification(workflow: WorkflowState) -> None:
    workflow.status = WorkflowStatus.RUNNING
    workflow.suspended_trace_id = None
    touch_workflow(workflow)


def start_analysis(workflow: WorkflowState, *, reset_clarify: bool = True) -> str:
    analysis_id = str(uuid4())
    workflow.active_analysis_id = analysis_id
    workflow.progress_step = "starting"
    workflow.status = WorkflowStatus.RUNNING
    if reset_clarify:
        workflow.clarify_round = 0
    workflow.sql_attempt = 1
    workflow.steps = []
    # Fresh agent-call budget per analysis so multi-turn follow-ups are not
    # blocked by prior runs (curator + ingress + pipeline share the same caps).
    workflow.budget_spent = {}
    if analysis_id not in workflow.analysis_history:
        workflow.analysis_history.append(analysis_id)
    touch_workflow(workflow)
    return analysis_id


def resume_analysis(workflow: WorkflowState) -> None:
    """Continue an in-flight analysis without resetting clarify_round."""
    workflow.status = WorkflowStatus.RUNNING
    workflow.suspended_trace_id = None
    touch_workflow(workflow)
