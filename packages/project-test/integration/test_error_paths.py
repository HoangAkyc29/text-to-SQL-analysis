"""Error handling and AnalysisOutcome coverage."""

from __future__ import annotations

import pytest

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.workflow import AnalysisOutcome
from project_core.domain.errors.codes import (
    AgentUnavailableError,
    BudgetExceededError,
    ClarifyRoundsExceededError,
    ContractInvalidError,
    LLMProviderError,
    PolicyViolationError,
    ProjectError,
    WorkflowStaleError,
)
from project_core.domain.feedback.satisfaction_rules import detect_satisfaction
from project_core.domain.sql.result_profile import build_result_profile
from project_core.domain.workflow.outcomes import is_case_study_eligible, is_negative_example
from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
from project_test.helpers.stub_sql import StubSqlGateway

pytestmark = pytest.mark.integration


def test_error_codes_have_stable_strings():
    assert ClarifyRoundsExceededError.code == "CLARIFY_ROUNDS_EXCEEDED"
    assert PolicyViolationError.code == "POLICY_VIOLATION"
    assert AgentUnavailableError.code == "AGENT_UNAVAILABLE"


def test_clarify_rounds_exceeded_is_project_error():
    err = ClarifyRoundsExceededError("max")
    assert isinstance(err, ProjectError)


def test_outcome_eligibility_matrix():
    assert is_case_study_eligible(AnalysisOutcome.SUCCESS.value)
    assert not is_case_study_eligible(AnalysisOutcome.IMPOSSIBLE.value)
    assert is_negative_example(AnalysisOutcome.EMPTY.value)


def test_satisfaction_negative_detected():
    sig = detect_satisfaction("sai rồi số lạ quá")
    assert sig is not None
    assert sig["sentiment"] == "negative"


def test_satisfaction_positive_detected():
    sig = detect_satisfaction("cảm ơn chuẩn rồi")
    assert sig is not None
    assert sig["sentiment"] == "positive"


def test_result_profile_flags_empty():
    import pandas as pd

    profile = build_result_profile(pd.DataFrame())
    assert "empty" in profile.flags


def test_pipeline_IV_impossible_outcome(pipeline_factory, workflow_state, hq_permissions):
    invoker = ScriptedAgentInvoker(
        {
            "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 10 sale_id FROM sales"]}],
            "III": [{"verdict": "approve"}],
            "IV": [{"action": "impossible", "reason": "metric not in schema"}],
        }
    )
    result = pipeline_factory(invoker, StubSqlGateway()).run(
        brief=AnalysisBrief(intent="x"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    assert result.outcome == AnalysisOutcome.IMPOSSIBLE.value


def test_stub_sql_policy_block_path():
    sql = StubSqlGateway(policy_block=True)
    result = sql.execute_readonly("SELECT 1", "u")
    assert result.get("error") == "policy_blocked" or result.get("violations")
