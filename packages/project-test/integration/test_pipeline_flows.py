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
    assert invoker.agents_called() == ["II", "II", "III", "IV"]
    assert invoker.calls[0]["metadata"].get("mode") == "select_tables"
    assert invoker.calls[1]["metadata"].get("mode") == "plan_sql"
    assert invoker.calls[1]["payload"]["inbox"].get("table_samples")
    assert any(s.step_type == WorkflowStepType.SELECT_TABLES for s in result.workflow_steps)


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
                {
                    "action": "plan_sql",
                    "sql_queries": [
                        "SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRAN_DATE >= '2026-07-01'"
                    ],
                    "query_meta": [{"role": "main", "purpose": "qty_agg"}],
                },
                {
                    "action": "plan_sql",
                    "sql_queries": [
                        "SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"
                    ],
                    "query_meta": [{"role": "main", "purpose": "qty_agg"}],
                },
            ],
            # max_risk_retries=2 → two rejects exhaust III loop, then II sql_attempt 2.
            "III": [
                {
                    "verdict": "reject",
                    "concerns": ["ambiguous_fact_join_grain"],
                    "risk_feedback": {
                        "issue": "join_grain",
                        "suggestion": "Align join keys with schema",
                    },
                },
                {
                    "verdict": "reject",
                    "concerns": ["ambiguous_fact_join_grain"],
                    "risk_feedback": {
                        "issue": "join_grain",
                        "suggestion": "Align join keys with schema",
                    },
                },
                {"verdict": "approve"},
            ],
            "IV": [{"action": "complete", "headline_metrics": {}, "artifact_paths": []}],
        }
    )
    result = pipeline_factory(invoker, StubSqlGateway()).run(
        brief=AnalysisBrief(intent="sales"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    assert result.outcome == AnalysisOutcome.SUCCESS.value
    plan_calls = [
        c
        for c in invoker.calls
        if c["agent"] == "II" and c["metadata"].get("mode") == "plan_sql"
    ]
    assert len(plan_calls) >= 2
    retry_inbox = plan_calls[1]["payload"].get("inbox") or {}
    assert retry_inbox.get("risk_feedback", {}).get("issue") == "join_grain"
    rejections = retry_inbox.get("risk_rejections") or []
    assert len(rejections) >= 1
    assert rejections[0]["issue"] == "join_grain"
    assert rejections[0]["purpose"] == "qty_agg"
    assert "rejected_sql" in rejections[0]
    assert any(s.step_type == WorkflowStepType.RISK_REJECT for s in result.workflow_steps)


def test_pipeline_risk_reject_accumulates_multi_query(pipeline_factory, workflow_state, hq_permissions):
    invoker = ScriptedAgentInvoker(
        {
            "II": [
                {
                    "action": "plan_sql",
                    "sql_queries": [
                        "SELECT TOP 10 SKU_ID FROM STRANS WHERE TRAN_DATE >= '2026-07-01'",
                        "SELECT TOP 10 TRANS_NUM FROM TRANSHDR WHERE TRAN_DATE >= '2026-07-01'",
                    ],
                    "query_meta": [
                        {"role": "main", "purpose": "qty_agg"},
                        {"role": "main", "purpose": "top_n_bills"},
                    ],
                    "target_dbs": ["db2", "db2"],
                },
                {
                    "action": "plan_sql",
                    "sql_queries": [
                        "SELECT TOP 10 SKU_ID FROM STRANS WHERE TRANS_CODE = '113'"
                    ],
                    "query_meta": [{"role": "main", "purpose": "qty_agg"}],
                },
            ],
            # Each query: 2 rejects (max_risk_retries) → 4 rejects, then approve on attempt 2.
            "III": [
                {
                    "verdict": "reject",
                    "concerns": ["a"],
                    "risk_feedback": {"issue": "issue_q0"},
                },
                {
                    "verdict": "reject",
                    "concerns": ["a"],
                    "risk_feedback": {"issue": "issue_q0"},
                },
                {
                    "verdict": "reject",
                    "concerns": ["b"],
                    "risk_feedback": {"issue": "issue_q1"},
                },
                {
                    "verdict": "reject",
                    "concerns": ["b"],
                    "risk_feedback": {"issue": "issue_q1"},
                },
                {"verdict": "approve"},
            ],
            "IV": [{"action": "complete", "headline_metrics": {}, "artifact_paths": []}],
        }
    )
    result = pipeline_factory(invoker, StubSqlGateway()).run(
        brief=AnalysisBrief(intent="sales two deliverables"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    assert result.outcome == AnalysisOutcome.SUCCESS.value
    plan_calls = [
        c
        for c in invoker.calls
        if c["agent"] == "II" and c["metadata"].get("mode") == "plan_sql"
    ]
    retry_inbox = plan_calls[1]["payload"].get("inbox") or {}
    rejections = retry_inbox.get("risk_rejections") or []
    assert len(rejections) == 2
    assert rejections[0]["purpose"] == "qty_agg"
    assert rejections[0]["issue"] == "issue_q0"
    assert rejections[1]["purpose"] == "top_n_bills"
    assert rejections[1]["issue"] == "issue_q1"
    assert retry_inbox["risk_feedback"]["issue"] == "issue_q1"

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
    assert len(ii_calls) == 4  # select+plan per attempt
    plan_calls = [c for c in ii_calls if c["metadata"].get("mode") == "plan_sql"]
    assert len(plan_calls) == 2
    for pc in plan_calls:
        samples = pc["payload"].get("inbox", {}).get("table_samples")
        assert samples, "table_samples must be attached before every plan_sql (incl. IV retry)"
    assert "data_feedback" in str(plan_calls[1]["payload"].get("inbox", {})) or plan_calls[1]["payload"].get("attempt") == 2


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
