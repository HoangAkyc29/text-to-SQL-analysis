"""Pipeline SQL audit logging."""

from __future__ import annotations

import pytest

from project_core.domain.audit.logger import AuditLogger
from project_core.domain.contracts.brief import AnalysisBrief
from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
from project_test.helpers.stub_sql import StubSqlGateway

pytestmark = pytest.mark.integration


def test_pipeline_emits_sql_execute_audit(pipeline_factory, workflow_state, hq_permissions):
    audit = AuditLogger()
    invoker = ScriptedAgentInvoker(
        {
            "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]}],
            "III": [{"verdict": "approve"}],
            "IV": [{"action": "complete", "headline_metrics": {}, "artifact_paths": []}],
        }
    )
    pipeline = pipeline_factory(invoker, StubSqlGateway())
    pipeline.audit = audit
    pipeline.run(brief=AnalysisBrief(intent="x"), workflow=workflow_state, permissions=hq_permissions)
    assert any(e["event_type"] == "sql_execute" for e in audit.events())


def test_pipeline_emits_agent_ii_plan_audit(pipeline_factory, workflow_state, hq_permissions):
    audit = AuditLogger()
    sql = "SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"
    invoker = ScriptedAgentInvoker(
        {
            "II": [
                {
                    "action": "plan_sql",
                    "sql_queries": [sql],
                    "query_meta": [{"role": "main", "purpose": "sales"}],
                    "target_dbs": ["db2"],
                    "reasoning": "Fact query STRANS sales",
                }
            ],
            "III": [{"verdict": "approve"}],
            "IV": [{"action": "complete", "headline_metrics": {}, "artifact_paths": []}],
        }
    )
    pipeline = pipeline_factory(invoker, StubSqlGateway())
    pipeline.audit = audit
    pipeline.run(brief=AnalysisBrief(intent="x"), workflow=workflow_state, permissions=hq_permissions)
    plan_events = [e for e in audit.events() if e["event_type"] == "agent_ii_plan"]
    assert len(plan_events) == 2  # select_tables + plan_sql
    sql_plans = [e for e in plan_events if e["payload"].get("action") == "plan_sql"]
    assert len(sql_plans) == 1
    payload = sql_plans[0]["payload"]
    assert payload["queries"][0]["sql"] == sql
    assert payload["reasoning"] == "Fact query STRANS sales"
    assert any(s.step_type.value == "select_tables" for s in workflow_state.steps)
    assert any(s.step_type.value == "plan_sql" for s in workflow_state.steps)
