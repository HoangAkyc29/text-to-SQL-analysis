"""explain_sql must use per-query target_db (tdb), not plan default_db."""

from __future__ import annotations

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.sql_acl import SqlAclContext
from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
from project_test.helpers.stub_sql import StubSqlGateway

import pytest

pytestmark = pytest.mark.integration


def test_explain_sql_uses_query_target_db(pipeline_factory, workflow_state, hq_permissions):
    explain_dbs: list[str] = []

    class _Sql(StubSqlGateway):
        def explain_sql(self, sql: str, acl: SqlAclContext, *, target_db: str = "db2") -> dict:
            explain_dbs.append(target_db)
            return {"status": "ok", "plan_rows": 1}

    invoker = ScriptedAgentInvoker(
        {
            "II": [
                {
                    "action": "plan_sql",
                    "sql_queries": ["SELECT TOP 10 SKU_ID FROM STRANS WHERE TRANS_CODE = '113'"],
                    "target_dbs": ["db1"],
                    "target_db": "db2",
                }
            ],
            "III": [
                {"verdict": "reject", "risk_feedback": {"issue": "performance scan"}, "needs_explain": True},
                {"verdict": "approve"},
            ],
            "IV": [{"action": "complete", "headline_metrics": {}, "artifact_paths": []}],
        }
    )
    pipeline_factory(invoker, _Sql()).run(
        brief=AnalysisBrief(intent="x"),
        workflow=workflow_state,
        permissions=hq_permissions,
    )
    assert explain_dbs == ["db1"]
