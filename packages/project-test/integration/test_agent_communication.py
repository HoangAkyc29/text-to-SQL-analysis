"""Verify ordered agent-to-agent handoffs through pipeline invoke log."""

from __future__ import annotations

import pytest

from project_core.domain.contracts.brief import AnalysisBrief
from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
from project_test.helpers.stub_sql import StubSqlGateway

pytestmark = pytest.mark.integration


def test_communication_II_to_III_to_IV_order(pipeline_factory, workflow_state, hq_permissions):
    invoker = ScriptedAgentInvoker(
        {
            "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 5 SKU_ID FROM STRANS WHERE TRANS_CODE = '113'"]}],
            "III": [{"verdict": "approve"}],
            "IV": [{"action": "complete", "headline_metrics": {}, "artifact_paths": []}],
        }
    )
    pipeline_factory(invoker, StubSqlGateway()).run(
        brief=AnalysisBrief(intent="sales"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    assert invoker.agents_called()[:3] == ["II", "III", "IV"]


def test_communication_III_receives_sql_from_II(pipeline_factory, workflow_state, hq_permissions):
    invoker = ScriptedAgentInvoker(
        {
            "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 1 SKU_ID FROM STRANS WHERE TRANS_CODE = '113'"]}],
            "III": [{"verdict": "approve"}],
            "IV": [{"action": "complete", "headline_metrics": {}, "artifact_paths": []}],
        }
    )
    pipeline_factory(invoker, StubSqlGateway()).run(
        brief=AnalysisBrief(intent="x"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    iii_call = invoker.last_call("III")
    assert iii_call is not None
    assert "sql" in str(iii_call["payload"]) or "SELECT" in str(iii_call)


def test_communication_IV_receives_dataset_manifest(pipeline_factory, workflow_state, hq_permissions):
    invoker = ScriptedAgentInvoker(
        {
            "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]}],
            "III": [{"verdict": "approve"}],
            "IV": [{"action": "complete", "headline_metrics": {"rows": 1}, "artifact_paths": []}],
        }
    )
    pipeline_factory(invoker, StubSqlGateway(rows=[{"sale_id": 1}])).run(
        brief=AnalysisBrief(intent="x"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    iv_call = invoker.last_call("IV")
    assert "dataset_manifest" in iv_call["payload"] or "result_profile" in iv_call["payload"]


def test_communication_IV_to_II_data_feedback_inbox(pipeline_factory, workflow_state, hq_permissions):
    invoker = ScriptedAgentInvoker(
        {
            "II": [
                {"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]},
                {"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]},
            ],
            "III": [{"verdict": "approve"}, {"verdict": "approve"}],
            "IV": [
                {"action": "data_feedback", "data_feedback": {"needs_sql_retry": True, "issue": "empty", "summary": "retry"}},
                {"action": "complete", "headline_metrics": {}, "artifact_paths": []},
            ],
        }
    )
    pipeline_factory(invoker, StubSqlGateway()).run(
        brief=AnalysisBrief(intent="x"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    second_ii = [c for c in invoker.calls if c["agent"] == "II"][1]
    inbox = second_ii["payload"].get("inbox", {})
    assert "data_feedback" in inbox


def test_communication_I_not_in_pipeline_invoke(pipeline_factory, workflow_state, hq_permissions):
    """Agent I is gateway-facing; pipeline only calls II/III/IV."""
    invoker = ScriptedAgentInvoker(
        {
            "II": [{"action": "impossible", "reason": "x"}],
        }
    )
    pipeline_factory(invoker, StubSqlGateway()).run(
        brief=AnalysisBrief(intent="x"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    assert "I" not in invoker.agents_called()


def test_communication_sql_gateway_executes_after_III_approve(pipeline_factory, workflow_state, hq_permissions):
    sql = StubSqlGateway(rows=[{"sale_id": 99}])
    invoker = ScriptedAgentInvoker(
        {
            "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]}],
            "III": [{"verdict": "approve"}],
            "IV": [{"action": "complete", "headline_metrics": {}, "artifact_paths": []}],
        }
    )
    pipeline_factory(invoker, sql).run(
        brief=AnalysisBrief(intent="x"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    assert len(sql.executed) >= 1
