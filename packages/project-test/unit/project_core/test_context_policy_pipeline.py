"""ContextPolicy integration with pipeline tool grants and schema filter."""

from __future__ import annotations

from project_core.domain.access.context_policy import ContextPolicy
from project_core.domain.access.acl import build_permissions_snapshot
from project_core.domain.contracts.workflow import AnalysisOutcome
from project_core.orchestration.pipeline import SupermarketAnalysisPipeline
from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
from project_test.helpers.stub_sql import StubSqlGateway


def test_filter_schema_excerpt_respects_allowed_tables(schema_catalog):
    policy = ContextPolicy()
    perms = build_permissions_snapshot("u", "hq_analyst")
    snapshot = schema_catalog.snapshot()
    filtered = policy.filter_schema_excerpt("II", perms, snapshot)
    for key in filtered:
        assert key.lower() in {t.lower() for t in perms.allowed_tables}


def test_is_tool_allowed_per_agent():
    policy = ContextPolicy()
    assert policy.is_tool_allowed("III", "explain_sql")
    assert not policy.is_tool_allowed("II", "export_excel")


class _DenyExplainSqlGateway(StubSqlGateway):
    def explain_sql(self, sql: str, actor_id: str) -> dict:
        return {"plan": "mock"}


def test_pipeline_explain_sql_on_performance_reject(pipeline_factory, workflow_state, hq_permissions):
    from project_core.domain.contracts.brief import AnalysisBrief

    calls: list[str] = []

    class _TrackingSql(_DenyExplainSqlGateway):
        def explain_sql(self, sql: str, actor_id: str) -> dict:
            calls.append("explain")
            return {"estimated_rows": 99999}

    invoker = ScriptedAgentInvoker(
        {
            "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]}],
            "III": [
                {"verdict": "reject", "risk_feedback": {"issue": "full table scan detected"}, "needs_explain": True},
                {"verdict": "approve"},
            ],
            "IV": [{"action": "complete", "headline_metrics": {"rows": 1}, "artifact_paths": []}],
        }
    )
    pipeline = pipeline_factory(invoker, _TrackingSql())
    result = pipeline.run(brief=AnalysisBrief(intent="x"), workflow=workflow_state, permissions=hq_permissions)
    assert calls == ["explain"]
    assert result.outcome == AnalysisOutcome.SUCCESS.value
