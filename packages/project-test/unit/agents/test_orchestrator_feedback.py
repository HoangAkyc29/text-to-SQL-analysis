"""Orchestrator wires satisfaction and behavioral feedback."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from chat_gateway.orchestrator import ChatOrchestrator
from project_core.domain.contracts.feedback import SatisfactionSignal
from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
from project_test.helpers.stub_sql import StubSqlGateway


def test_satisfaction_signal_calls_feedback_loop(fake_redis):
    feedback = MagicMock()
    orch = ChatOrchestrator()
    orch.feedback = feedback

    bundle = orch.stm.load_session("fb-1")
    from project_core.domain.workflow.state import new_workflow, start_analysis

    bundle.workflow = new_workflow("fb-1", "u1")
    start_analysis(bundle.workflow)
    bundle.workflow.last_completed_trace_id = "trace-prev"
    orch.stm.save_workflow("fb-1", bundle.workflow)

    stub = ScriptedAgentInvoker(
        {
            "I": [
                {
                    "route": "chitchat",
                    "user_message": "cảm ơn",
                    "satisfaction_signal": {"sentiment": "positive", "confidence": 0.9},
                },
            ],
        }
    )
    with patch("chat_gateway.orchestrator.HttpAgentInvoker", return_value=stub):
        orch.handle_chat(session_id="fb-1", message="cảm ơn chuẩn rồi", user={"sub": "u1", "role": "hq_analyst"})

    feedback.on_satisfaction_signal.assert_called_once()
    signal = feedback.on_satisfaction_signal.call_args[0][0]
    assert isinstance(signal, SatisfactionSignal)
    assert signal.applies_to_trace_id == "trace-prev"


def test_artifact_download_behavioral_signal(fake_redis):
    feedback = MagicMock()
    orch = ChatOrchestrator()
    orch.feedback = feedback
    orch.record_artifact_download("sess-dl", "trace-dl")
    feedback.on_behavioral_signal.assert_called_once()
    assert feedback.on_behavioral_signal.call_args[0][1].signal_type == "download"
