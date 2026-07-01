"""SessionTraceBudget and shared pipeline budget."""

from __future__ import annotations

import pytest

from project_core.domain.budget import SessionTraceBudget, TraceBudget
from project_core.domain.errors.codes import BudgetExceededError
from project_core.orchestration.pipeline import SupermarketAnalysisPipeline
from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
from project_test.helpers.stub_sql import StubSqlGateway


def test_session_budget_records_agent_i():
    budget = SessionTraceBudget()
    budget.record("I")
    assert budget.trace_budget.spent["I"] == 1


def test_session_budget_enforces_cap(monkeypatch):
    from project_core.config.loader import load_project_config

    cfg = load_project_config()
    cfg.budget.agent_caps["I"] = 1
    monkeypatch.setattr("project_core.domain.budget.load_project_config", lambda: cfg)

    budget = SessionTraceBudget()
    budget.record("I")
    with pytest.raises(BudgetExceededError):
        budget.record("I")


def test_pipeline_uses_shared_trace_budget(pipeline_factory, workflow_state, hq_permissions):
    shared = TraceBudget()
    shared.charge("I", calls=2)
    invoker = ScriptedAgentInvoker(
        {
            "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]}],
            "III": [{"verdict": "approve"}],
            "IV": [{"action": "complete", "headline_metrics": {"rows": 1}, "artifact_paths": []}],
        }
    )
    pipeline = pipeline_factory(invoker, StubSqlGateway())
    pipeline.run(
        brief=__import__("project_core.domain.contracts.brief", fromlist=["AnalysisBrief"]).AnalysisBrief(intent="x"),
        workflow=workflow_state,
        permissions=hq_permissions,
        trace_budget=shared,
    )
    assert shared.spent["I"] == 2
    assert shared.spent["II"] >= 1
    assert shared.spent["IV"] >= 1


def test_orchestrator_syncs_budget_spent(fake_redis):
    from chat_gateway.orchestrator import ChatOrchestrator
    from unittest.mock import patch
    from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
    from project_test.helpers.stub_sql import StubSqlGateway

    stub = ScriptedAgentInvoker(
        {
            "I": [
                {"route": "analysis", "user_message": "ok", "brief": {"intent": "VIP", "filters": {"card_prefix": "E"}}},
                {"user_message": "done", "artifacts": []},
            ],
            "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]}],
            "III": [{"verdict": "approve"}],
            "IV": [{"action": "complete", "headline_metrics": {"rows": 1}, "artifact_paths": []}],
        }
    )
    sql = StubSqlGateway()
    with patch("chat_gateway.orchestrator.HttpAgentInvoker", return_value=stub), patch(
        "chat_gateway.orchestrator.HttpSqlGatewayClient", return_value=sql
    ):
        orch = ChatOrchestrator()
        orch.pipeline.agent_invoker = stub
        orch.pipeline.sql_gateway = sql
        resp = orch.handle_chat(session_id="budget-sess", message="Phan tich VIP doanh thu", user={"sub": "u1", "role": "hq_analyst"})
    wf = orch.stm.load_session("budget-sess").workflow
    assert wf is not None
    assert wf.budget_spent.get("I", 0) >= 1
    assert wf.budget_spent.get("II", 0) >= 1
    assert wf.budget_spent.get("IV", 0) >= 1
    assert resp.outcome == "success"
