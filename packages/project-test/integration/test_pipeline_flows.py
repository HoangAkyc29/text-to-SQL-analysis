"""SupermarketAnalysisPipeline end-to-end flows with scripted agents."""

from __future__ import annotations

import pytest

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.workflow import AnalysisOutcome, WorkflowStepType
from project_core.domain.errors.codes import ClarifyRoundsExceededError
from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
from project_test.helpers.stub_sql import StubSqlGateway

pytestmark = pytest.mark.integration


def _happy_scripts():
    return {
        "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]}],
        "III": [{"verdict": "approve", "concerns": []}],
        "IV": [{"action": "complete", "headline_metrics": {"rows": 1}, "artifact_paths": ["out/a.xlsx"]}],
    }


def test_pipeline_success_happy_path(pipeline_factory, workflow_state, hq_permissions):
    invoker = ScriptedAgentInvoker(_happy_scripts())
    pipeline = pipeline_factory(invoker, StubSqlGateway())
    result = pipeline.run(
        brief=AnalysisBrief(intent="revenue by store"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    assert result.outcome == AnalysisOutcome.SUCCESS.value
    assert invoker.agents_called() == ["II", "III", "IV"]


def test_pipeline_needs_clarification(pipeline_factory, workflow_state, hq_permissions):
    invoker = ScriptedAgentInvoker(
        {"II": [{"action": "clarify", "clarification_request": {
            "reason": "missing",
            "partial_brief": {"intent": "VIP"},
            "questions": [{"id": "q1", "prompt": "?", "options": [], "maps_to_brief_field": "filters.x"}],
        }}]}
    )
    result = pipeline_factory(invoker, StubSqlGateway()).run(
        brief=AnalysisBrief(intent="VIP"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    assert result.outcome == AnalysisOutcome.NEEDS_CLARIFICATION.value
    assert result.needs_clarification is not None


def test_pipeline_II_impossible(pipeline_factory, workflow_state, hq_permissions):
    invoker = ScriptedAgentInvoker({"II": [{"action": "impossible", "reason": "no schema"}]})
    result = pipeline_factory(invoker, StubSqlGateway()).run(
        brief=AnalysisBrief(intent="margin by planet"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    assert result.outcome == AnalysisOutcome.IMPOSSIBLE.value


def test_pipeline_risk_reject_then_retry(pipeline_factory, workflow_state, hq_permissions):
    invoker = ScriptedAgentInvoker(
        {
            "II": [
                {"action": "plan_sql", "sql_queries": ["SELECT bad_col FROM STRANS"]},
                {"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]},
            ],
            "III": [{"verdict": "reject", "risk_feedback": {"issue": "scan"}}, {"verdict": "approve"}],
            "IV": [{"action": "complete", "headline_metrics": {}, "artifact_paths": []}],
        }
    )
    result = pipeline_factory(invoker, StubSqlGateway()).run(
        brief=AnalysisBrief(intent="sales"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    assert result.outcome == AnalysisOutcome.SUCCESS.value
    assert invoker.calls[0]["agent"] == "II"
    assert invoker.calls[1]["agent"] == "III"


def test_pipeline_IV_data_feedback_loop(pipeline_factory, workflow_state, hq_permissions):
    invoker = ScriptedAgentInvoker(
        {
            "II": [
                {"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]},
                {"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]},
            ],
            "III": [{"verdict": "approve"}, {"verdict": "approve"}],
            "IV": [
                {"action": "data_feedback", "data_feedback": {"needs_sql_retry": True, "issue": "grain", "summary": "wrong grain"}},
                {"action": "complete", "headline_metrics": {"rows": 2}, "artifact_paths": ["out/b.xlsx"]},
            ],
        }
    )
    result = pipeline_factory(invoker, StubSqlGateway()).run(
        brief=AnalysisBrief(intent="sales detail"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    assert result.outcome == AnalysisOutcome.SUCCESS.value
    ii_calls = [c for c in invoker.calls if c["agent"] == "II"]
    assert len(ii_calls) == 2
    assert "data_feedback" in str(ii_calls[1]["payload"].get("inbox", {})) or ii_calls[1]["payload"].get("attempt") == 2


def test_pipeline_policy_blocked_exhausted(pipeline_factory, workflow_state, hq_permissions):
    invoker = ScriptedAgentInvoker(
        {"II": [{"action": "plan_sql", "sql_queries": ["SELECT * FROM forbidden_planet"]}] * 3}
    )
    sql = StubSqlGateway()
    result = pipeline_factory(invoker, sql).run(
        brief=AnalysisBrief(intent="x"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    assert result.outcome in {AnalysisOutcome.POLICY_BLOCKED.value, AnalysisOutcome.ERROR.value}


def test_pipeline_clarify_rounds_exceeded(pipeline_factory, workflow_state, hq_permissions):
    clarify = {
        "action": "clarify",
        "clarification_request": {
            "reason": "r",
            "partial_brief": {"intent": "VIP"},
            "questions": [{"id": "q", "prompt": "?", "options": [], "maps_to_brief_field": "filters.x"}],
        },
    }
    invoker = ScriptedAgentInvoker({"II": [clarify] * 5})
    workflow_state.clarify_round = 3
    with pytest.raises(ClarifyRoundsExceededError):
        pipeline_factory(invoker, StubSqlGateway()).run(
            brief=AnalysisBrief(intent="VIP"),
            workflow=workflow_state,
            permissions=hq_permissions,
        )


def test_pipeline_stages_case_study_on_success(pipeline_factory, workflow_state, hq_permissions, feedback_loop):
    invoker = ScriptedAgentInvoker(_happy_scripts())
    pipeline = pipeline_factory(invoker, StubSqlGateway(), feedback_loop=feedback_loop)
    result = pipeline.run(
        brief=AnalysisBrief(intent="revenue"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    assert feedback_loop.indexer.find_by_trace(result.trace_id) is not None
