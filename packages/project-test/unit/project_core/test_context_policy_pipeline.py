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


def test_retry_directive_routes_missing_value_and_ranking_evidence():
    from project_core.domain.contracts.brief import AnalysisBrief, BriefRequirement
    from project_core.domain.contracts.feedback import DataFeedback, MissingForBrief
    from project_core.domain.contracts.pipeline import ColumnStat, ResultProfile
    from project_core.orchestration.pipeline import _build_retry_directive

    brief = AnalysisBrief(
        requirements=[
            BriefRequirement(
                requirement_id="filter:0",
                kind="filter",
                key="item_code",
                source="explicit",
                required=True,
                value=["A-1"],
            ),
            BriefRequirement(
                requirement_id="ranking:0",
                kind="ranking",
                key="top_n",
                source="explicit",
                required=True,
                value={
                    "limit": 2,
                    "partition_by": "item",
                    "order_by": "time",
                    "direction": "desc",
                },
            ),
        ]
    )
    feedback = DataFeedback(
        issue="insufficient_deliverable",
        summary="missing evidence",
        missing_for_brief=[
            MissingForBrief(
                brief_field="missing_filter:item_code",
                reason="not present",
            ),
            MissingForBrief(
                brief_field="missing_ranking:ranking:0",
                reason="not present",
            ),
        ],
    )
    directive = _build_retry_directive(
        feedback=feedback,
        coverage={
            "gaps": [
                "missing_filter:item_code",
                "missing_ranking:ranking:0",
            ]
        },
        brief=brief,
        profiles=[
            ResultProfile(
                row_count=4,
                columns=[ColumnStat(name="internal_item_id")],
            )
        ],
        query_meta=[{"purpose": "detail", "requirement_ids": ["ranking:0"]}],
        sql_attempt=1,
        plan_fingerprint="abc",
    )
    assert directive["retry_target"] == "agent_ii"
    assert directive["must_fix_requirement_ids"] == ["filter:0", "ranking:0"]
    assert directive["prior_result_profiles"][0]["columns"] == ["internal_item_id"]
    assert directive["must_change_plan"] is True


def test_sql_plan_fingerprint_ignores_formatting_only_changes():
    from project_core.orchestration.pipeline import _sql_plan_fingerprint

    first = _sql_plan_fingerprint(
        ["SELECT  value\nFROM source"],
        ["db2"],
        [{"role": "main", "purpose": "metric", "requirement_ids": ["metric:0"]}],
    )
    second = _sql_plan_fingerprint(
        [" select VALUE from SOURCE "],
        ["db2"],
        [{"purpose": "renamed_metric", "role": "main", "requirement_ids": ["metric:1"]}],
    )
    assert first == second
