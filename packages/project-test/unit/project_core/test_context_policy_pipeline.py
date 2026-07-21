"""ContextPolicy integration with pipeline tool grants and schema filter."""

from __future__ import annotations

from project_core.domain.access.context_policy import ContextPolicy
from project_core.domain.access.acl import build_permissions_snapshot
from project_core.domain.contracts.sql_acl import SqlAclContext
from project_core.domain.contracts.workflow import AnalysisOutcome
from project_core.orchestration.pipeline import SupermarketAnalysisPipeline
from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
from project_test.helpers.stub_sql import StubSqlGateway


def test_filter_schema_excerpt_respects_allowed_tables(schema_catalog):
    policy = ContextPolicy()
    perms = build_permissions_snapshot("u", "hq_analyst")
    snapshot = schema_catalog.snapshot()
    filtered = policy.filter_schema_excerpt(perms, snapshot)
    for key in filtered:
        assert key.lower() in {t.lower() for t in perms.allowed_tables}


def test_is_tool_allowed_per_agent():
    policy = ContextPolicy()
    assert policy.is_tool_allowed("III", "explain_sql")
    assert not policy.is_tool_allowed("II", "export_excel")


def test_can_invoke_tool_respects_grants():
    policy = ContextPolicy()
    from project_core.domain.access.acl import build_permissions_snapshot

    perms = build_permissions_snapshot("u", "hq_analyst")
    perms = perms.model_copy(update={"tool_grants": ["tool:sql-gateway:validate"]})
    assert policy.can_invoke_tool(perms, "II", "validate_sql")
    assert not policy.can_invoke_tool(perms, "III", "explain_sql")
    assert policy.can_execute_sql(perms) is False
    perms = perms.model_copy(update={"tool_grants": list(perms.tool_grants) + ["tool:sql-gateway:execute"]})
    assert policy.can_execute_sql(perms)


def test_tool_wildcard_grant_matches_all():
    policy = ContextPolicy()
    from project_core.domain.access.acl import build_permissions_snapshot

    perms = build_permissions_snapshot("u", "hq_analyst").model_copy(update={"tool_grants": ["tool:*"]})
    assert policy.can_invoke_tool(perms, "II", "validate_sql")
    assert policy.can_invoke_tool(perms, "III", "explain_sql")
    assert policy.can_execute_sql(perms)


def test_can_invoke_function_wildcard_and_specific():
    policy = ContextPolicy()
    from project_core.domain.access.acl import build_permissions_snapshot

    perms = build_permissions_snapshot("u", "hq_analyst")
    assert perms.allowed_functions == ["function:*"]
    assert policy.can_invoke_function(perms, "abc-123")

    restricted = perms.model_copy(update={"allowed_functions": ["function:abc-123"]})
    assert policy.can_invoke_function(restricted, "abc-123")
    assert not policy.can_invoke_function(restricted, "other-id")

    none = perms.model_copy(update={"allowed_functions": []})
    assert not policy.can_invoke_function(none, "abc-123")


class _DenyExplainSqlGateway(StubSqlGateway):
    def explain_sql(self, sql: str, acl: SqlAclContext, *, target_db: str = "db2") -> dict:
        return {"plan": "mock"}


def test_pipeline_explain_sql_on_performance_reject(pipeline_factory, workflow_state, hq_permissions):
    from project_core.domain.contracts.brief import AnalysisBrief

    calls: list[str] = []

    class _TrackingSql(_DenyExplainSqlGateway):
        def explain_sql(self, sql: str, acl: SqlAclContext, *, target_db: str = "db2") -> dict:
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
    # The explain path succeeds, but an unverified IV response cannot claim success.
    assert result.outcome == AnalysisOutcome.PARTIAL.value


def test_false_future_date_reject_uses_authoritative_clock():
    from project_core.domain.contracts.brief import AnalysisBrief, TimeRange
    from project_core.orchestration.pipeline import _is_false_future_date_reject

    stale_claim = {
        "concerns": ["future_date_query"],
        "issue": "future_date_query",
    }
    past_brief = AnalysisBrief(time_range=TimeRange(start="2020-01-01", end="2020-01-02"))
    future_brief = AnalysisBrief(time_range=TimeRange(start="2999-01-01", end="2999-01-02"))
    assert _is_false_future_date_reject(stale_claim, past_brief) is True
    assert _is_false_future_date_reject(stale_claim, future_brief) is False
    assert (
        _is_false_future_date_reject(
            {"concerns": ["unsafe_join"], "issue": "unsafe_join"},
            past_brief,
        )
        is False
    )
