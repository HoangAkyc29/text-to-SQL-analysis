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
