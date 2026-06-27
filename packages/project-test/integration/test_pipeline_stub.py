from __future__ import annotations

from typing import Any

from project_core.domain.access.acl import build_permissions_snapshot
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.orchestration.pipeline import SupermarketAnalysisPipeline


class _StubInvoker:
    def invoke(self, agent: str, payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        if agent == "II":
            return {"action": "impossible", "reason": "stub"}
        return {}


class _StubSql:
    def validate_sql(self, sql: str, actor_id: str) -> dict[str, Any]:
        return {"allowed": True, "sanitized_sql": sql}

    def explain_sql(self, sql: str, actor_id: str) -> dict[str, Any]:
        return {"status": "ok"}

    def execute_readonly(self, sql: str, actor_id: str) -> dict[str, Any]:
        return {"rows": [{"x": 1}], "columns": ["x"]}


def test_pipeline_stub_invoker():
    from project_core.domain.workflow.state import new_workflow

    wf = new_workflow("s1", "u1")
    wf.active_analysis_id = "a1"
    pipeline = SupermarketAnalysisPipeline(agent_invoker=_StubInvoker(), sql_gateway=_StubSql())
    result = pipeline.run(
        brief=AnalysisBrief(intent="test"),
        workflow=wf,
        permissions=build_permissions_snapshot("u1", "hq_analyst"),
    )
    assert result.outcome in {"impossible", "error", "policy_blocked"}
