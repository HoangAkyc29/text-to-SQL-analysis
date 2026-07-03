"""Pipeline sync deadline enforcement."""

from __future__ import annotations

import time

import pytest

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.workflow import AnalysisOutcome
from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
from project_test.helpers.stub_sql import StubSqlGateway

pytestmark = pytest.mark.integration


class _SlowInvoker(ScriptedAgentInvoker):
    def invoke(self, agent: str, payload: dict, metadata: dict) -> dict:
        time.sleep(0.05)
        return super().invoke(agent, payload, metadata)


def test_pipeline_sync_deadline_exceeded(pipeline_factory, workflow_state, hq_permissions):
    invoker = _SlowInvoker(
        {
            "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 1 SKU_ID FROM STRANS WHERE TRANS_CODE = '113'"]}],
            "III": [{"verdict": "approve"}],
            "IV": [{"action": "complete", "headline_metrics": {}, "artifact_paths": []}],
        }
    )
    pipeline = pipeline_factory(invoker, StubSqlGateway())
    result = pipeline.run(
        brief=AnalysisBrief(intent="x"),
        workflow=workflow_state,
        permissions=hq_permissions,
        deadline=time.monotonic() - 1,
    )
    assert result.outcome == AnalysisOutcome.ERROR.value
    assert any("sync_deadline_exceeded" in (c or "") for c in result.technical_summary.caveats)
