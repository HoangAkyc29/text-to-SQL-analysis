"""Workflow state machine helpers."""

from __future__ import annotations

import pytest

from project_core.domain.contracts.workflow import WorkflowStatus, WorkflowStep, WorkflowStepType
from project_core.domain.workflow.state import new_workflow, resume_after_clarification, start_analysis, suspend_for_clarification
from project_core.domain.workflow.steps import has_step_type, summarize_steps

pytestmark = pytest.mark.unit


def test_start_analysis_resets_counters():
    wf = new_workflow("s", "u")
    aid = start_analysis(wf)
    assert wf.active_analysis_id == aid
    assert wf.clarify_round == 0
    assert wf.status == WorkflowStatus.RUNNING


def test_suspend_and_resume_clarification():
    wf = new_workflow("s", "u")
    suspend_for_clarification(wf, "trace-1")
    assert wf.status == WorkflowStatus.AWAITING_CLARIFICATION
    resume_after_clarification(wf)
    assert wf.status == WorkflowStatus.RUNNING
    assert wf.suspended_trace_id is None


def test_summarize_steps_and_detect_data_feedback():
    steps = [
        WorkflowStep(step_id="1", trace_id="t", analysis_id="a", step_type=WorkflowStepType.EXECUTE, summary="ok"),
        WorkflowStep(step_id="2", trace_id="t", analysis_id="a", step_type=WorkflowStepType.DATA_FEEDBACK, summary="retry"),
    ]
    assert has_step_type(steps, WorkflowStepType.DATA_FEEDBACK)
    assert "data_feedback" in summarize_steps(steps)[1]
