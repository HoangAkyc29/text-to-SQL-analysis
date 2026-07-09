"""Unit tests for query role classification and pipeline terminal heuristics."""

from __future__ import annotations

import pytest

from project_core.domain.analysis.query_role_classifier import classify_query_roles
from project_core.domain.contracts.workflow import WorkflowStep, WorkflowStepType
from project_core.orchestration.pipeline import _synthesize_pre_iv_feedback, _terminal_on_exhausted

pytestmark = pytest.mark.unit


def test_classify_probe_only_success():
    mode, main_rows, probe_rows, main_idxs, probe_idxs = classify_query_roles(
        [{"role": "probe"}, {"role": "probe"}],
        {0: 3, 1: 0},
        num_queries=2,
    )
    assert mode == "probe_only_success"
    assert main_rows == 0
    assert probe_rows == 3
    assert main_idxs == []
    assert probe_idxs == [0, 1]


def test_classify_main_empty_probe_hit():
    mode, main_rows, probe_rows, _, _ = classify_query_roles(
        [{"role": "probe"}, {"role": "main"}],
        {0: 2, 1: 0},
        num_queries=2,
    )
    assert mode == "main_empty_probe_hit"
    assert main_rows == 0
    assert probe_rows == 2


def test_synthesize_pre_iv_skips_iv_on_probe_sql():
    from project_core.domain.contracts.brief import AnalysisBrief

    result = _synthesize_pre_iv_feedback(
        action="probe_sql",
        query_meta=[{"role": "probe"}],
        row_counts={0: 3},
        brief=AnalysisBrief(intent="gifts", filters={"product_code": "0030344"}),
        sql_attempt=1,
        max_sql_retries=3,
    )
    assert result.get("skip_iv") is True
    assert result["data_feedback"]["issue"] == "probe_success_needs_fact"


def test_terminal_on_exhausted_after_probe():
    steps = [
        WorkflowStep(
            step_id="1",
            trace_id="t",
            analysis_id="a",
            step_type=WorkflowStepType.EXECUTE,
            summary="rows=3;role=probe",
        ),
        WorkflowStep(
            step_id="2",
            trace_id="t",
            analysis_id="a",
            step_type=WorkflowStepType.DATA_FEEDBACK,
            summary="probe_success_needs_fact",
        ),
    ]
    from project_core.domain.contracts.workflow import WorkflowState

    wf = WorkflowState(session_id="s", actor_id="u1", steps=steps)
    terminal = _terminal_on_exhausted(wf)
    assert terminal is not None
    assert terminal[0].value == "empty"
