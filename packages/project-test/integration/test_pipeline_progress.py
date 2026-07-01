"""Pipeline progress_step persistence when poll_enabled."""

from __future__ import annotations

import pytest

from project_core.domain.contracts.brief import AnalysisBrief
from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
from project_test.helpers.stub_sql import StubSqlGateway

pytestmark = pytest.mark.integration


def test_pipeline_progress_callback(pipeline_factory, workflow_state, hq_permissions, monkeypatch):
    from project_core.config.loader import load_project_config

    cfg = load_project_config()
    cfg.pipeline.poll_enabled = True
    monkeypatch.setattr("project_core.orchestration.pipeline.load_project_config", lambda: cfg)

    steps_seen: list[str] = []

    def on_progress(wf):
        if wf.progress_step:
            steps_seen.append(wf.progress_step)

    invoker = ScriptedAgentInvoker(
        {
            "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]}],
            "III": [{"verdict": "approve"}],
            "IV": [{"action": "complete", "headline_metrics": {"rows": 1}, "artifact_paths": []}],
        }
    )
    pipeline = pipeline_factory(invoker, StubSqlGateway())
    pipeline.run(
        brief=AnalysisBrief(intent="x"),
        workflow=workflow_state,
        permissions=hq_permissions,
        on_progress=on_progress,
    )
    assert WorkflowStepType.PLAN_SQL.value in steps_seen
    assert WorkflowStepType.EXECUTE.value in steps_seen


from project_core.domain.contracts.workflow import WorkflowStepType  # noqa: E402
