"""Pipeline explain_sql integration."""

from __future__ import annotations

import pytest

from project_core.domain.contracts.brief import AnalysisBrief
from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
from project_test.helpers.stub_sql import StubSqlGateway

pytestmark = pytest.mark.integration


def test_pipeline_explain_path(pipeline_factory, workflow_state, hq_permissions):
    explain_calls: list[str] = []

    class _Sql(StubSqlGateway):
        def explain_sql(self, sql: str, actor_id: str) -> dict:
            explain_calls.append(sql)
            return {"plan": "index seek"}

    invoker = ScriptedAgentInvoker(
        {
            "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]}],
            "III": [
                {"verdict": "reject", "risk_feedback": {"issue": "performance scan"}, "needs_explain": True},
                {"verdict": "approve"},
            ],
            "IV": [{"action": "complete", "headline_metrics": {}, "artifact_paths": []}],
        }
    )
    pipeline = pipeline_factory(invoker, _Sql())
    pipeline.run(brief=AnalysisBrief(intent="x"), workflow=workflow_state, permissions=hq_permissions)
    assert len(explain_calls) == 1
