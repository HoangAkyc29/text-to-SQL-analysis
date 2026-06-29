"""Pydantic contract validation tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from project_core.domain.contracts.brief import AnalysisBrief, IntentSlice
from project_core.domain.contracts.clarification import ClarificationRequest
from project_core.domain.contracts.feedback import DataFeedback
from project_core.domain.contracts.pipeline import ResultProfile
from project_core.domain.contracts.workflow import WorkflowState, WorkflowStatus

pytestmark = pytest.mark.unit


def test_analysis_brief_roundtrip():
    brief = AnalysisBrief(intent="revenue", metrics=["revenue"], dimensions=["store"])
    restored = AnalysisBrief.model_validate(brief.model_dump())
    assert restored.intent == "revenue"


def test_intent_slice_from_brief():
    brief = AnalysisBrief(intent="x", metrics=["m1"], filters={"store_id": 1})
    sl = IntentSlice.from_brief(brief)
    assert sl.filters["store_id"] == 1


def test_clarification_request_source_must_be_II():
    req = ClarificationRequest(reason="r", partial_brief=AnalysisBrief(intent="a"), questions=[])
    assert req.source_agent == "II"


def test_data_feedback_requires_issue_and_summary():
    fb = DataFeedback(issue="empty", summary="no rows")
    assert fb.needs_sql_retry is True


def test_workflow_state_defaults_idle():
    wf = WorkflowState(session_id="s", actor_id="u")
    assert wf.status == WorkflowStatus.IDLE
    assert wf.clarify_round == 0
