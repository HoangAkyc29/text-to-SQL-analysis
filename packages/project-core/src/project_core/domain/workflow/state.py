from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from project_core.domain.contracts.workflow import WorkflowState, WorkflowStatus


def new_workflow(session_id: str, actor_id: str) -> WorkflowState:
    return WorkflowState(session_id=session_id, actor_id=actor_id)


def touch_workflow(workflow: WorkflowState) -> None:
    workflow.updated_at = datetime.utcnow()


def suspend_for_clarification(workflow: WorkflowState, trace_id: str) -> None:
    workflow.status = WorkflowStatus.AWAITING_CLARIFICATION
    workflow.suspended_trace_id = trace_id
    touch_workflow(workflow)


def resume_after_clarification(workflow: WorkflowState) -> None:
    workflow.status = WorkflowStatus.RUNNING
    workflow.suspended_trace_id = None
    touch_workflow(workflow)


def start_analysis(workflow: WorkflowState) -> str:
    analysis_id = str(uuid4())
    workflow.active_analysis_id = analysis_id
    workflow.status = WorkflowStatus.RUNNING
    workflow.clarify_round = 0
    workflow.sql_attempt = 1
    workflow.steps = []
    if analysis_id not in workflow.analysis_history:
        workflow.analysis_history.append(analysis_id)
    touch_workflow(workflow)
    return analysis_id
