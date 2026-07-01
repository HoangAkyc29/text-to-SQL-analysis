"""Gateway orchestrator wiring integration tests."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
from project_test.helpers.stub_sql import StubSqlGateway

pytestmark = pytest.mark.integration


def test_analysis_status_after_chat(fake_redis):
    from chat_gateway.orchestrator import ChatOrchestrator

    stub = ScriptedAgentInvoker(
        {
            "I": [
                {"route": "analysis", "user_message": "ok", "brief": {"intent": "VIP"}},
                {"user_message": "done"},
            ],
            "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 10 SKU_ID, AMOUNT FROM STRANS WHERE TRANS_CODE = '113'"]}],
            "III": [{"verdict": "approve"}],
            "IV": [{"action": "complete", "headline_metrics": {"rows": 1}, "artifact_paths": []}],
        }
    )
    orch = None
    with patch("chat_gateway.orchestrator.HttpAgentInvoker", return_value=stub), patch(
        "chat_gateway.orchestrator.HttpSqlGatewayClient", return_value=StubSqlGateway()
    ):
        orch = ChatOrchestrator()
        orch.pipeline.agent_invoker = stub
        orch.pipeline.sql_gateway = StubSqlGateway()
        resp = orch.handle_chat(session_id="status-sess", message="VIP doanh thu", user={"sub": "u1", "role": "hq_analyst"})

    assert orch is not None
    status = orch.analysis_status(resp.analysis_id or "")
    assert status["status"] != "unknown"
    assert status["status"] in {"idle", "running"}
    assert status.get("last_outcome") == "success"


def test_analysis_status_not_found(fake_redis):
    from chat_gateway.orchestrator import ChatOrchestrator

    status = ChatOrchestrator().analysis_status("nonexistent-id")
    assert status["status"] == "not_found"


def test_re_ask_behavioral_after_negative_outcome(fake_redis):
    from chat_gateway.orchestrator import ChatOrchestrator
    from project_core.domain.workflow.state import new_workflow, start_analysis
    from unittest.mock import MagicMock

    orch = ChatOrchestrator()
    feedback = MagicMock()
    orch.feedback = feedback
    bundle = orch.stm.load_session("reask-sess")
    bundle.workflow = new_workflow("reask-sess", "u1")
    start_analysis(bundle.workflow)
    bundle.workflow.brief = __import__(
        "project_core.domain.contracts.brief", fromlist=["AnalysisBrief"]
    ).AnalysisBrief(intent="VIP doanh thu tháng 3")
    bundle.workflow.last_outcome = "error"
    bundle.workflow.last_completed_trace_id = "t-old"
    orch.stm.save_workflow("reask-sess", bundle.workflow)

    stub = ScriptedAgentInvoker({"I": [{"route": "chitchat", "user_message": "ok"}]})
    with patch("chat_gateway.orchestrator.HttpAgentInvoker", return_value=stub):
        orch.handle_chat(session_id="reask-sess", message="VIP doanh thu tháng 3", user={"sub": "u1", "role": "hq_analyst"})

    feedback.on_behavioral_signal.assert_called()
    assert feedback.on_behavioral_signal.call_args[0][1].signal_type == "re_ask"
