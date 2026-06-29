"""chat-gateway HTTP surface with stub agents."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


@pytest.fixture
def gateway_client(monkeypatch, fake_redis):
    os.environ["ALLOW_LLM_STUB"] = "1"
    os.environ["ALLOW_DEV_AUTH"] = "1"
    os.environ["SQL_GATEWAY_INPROCESS"] = "1"
    from chat_gateway.app import app

    return TestClient(app)


def test_health(gateway_client):
    assert gateway_client.get("/health").json()["ok"] is True


def test_dev_login_issues_token(gateway_client):
    r = gateway_client.post("/auth/dev-login", json={"actor_id": "u1", "role": "hq_analyst"})
    assert "access_token" in r.json()


def test_chat_analysis_route(gateway_client, monkeypatch):
    """E2E-ish: gateway -> stub agents -> pipeline (in-process SQL)."""
    with patch("chat_gateway.orchestrator.HttpAgentInvoker") as mock_invoker_cls, patch(
        "chat_gateway.orchestrator.HttpSqlGatewayClient"
    ) as mock_sql_cls:
        from project_test.helpers.scripted_invoker import ScriptedAgentInvoker
        from project_test.helpers.stub_sql import StubSqlGateway

        stub = ScriptedAgentInvoker(
            {
                "I": [
                    {"route": "analysis", "user_message": "ok", "brief": {"intent": "VIP", "filters": {"card_prefix": "E"}}},
                    {"user_message": "done", "artifacts": []},
                ],
                "II": [{"action": "plan_sql", "sql_queries": ["SELECT TOP 10 sale_id FROM sales"]}],
                "III": [{"verdict": "approve"}],
                "IV": [{"action": "complete", "headline_metrics": {"rows": 1}, "artifact_paths": []}],
            }
        )
        mock_invoker_cls.return_value = stub
        mock_sql_cls.return_value = StubSqlGateway()
        r = gateway_client.post("/chat", json={"session_id": "gw-1", "message": "Phân tích VIP doanh thu"})
        assert r.status_code == 200
        body = r.json()
        assert body.get("outcome") == "success" or body.get("workflow_status") in {"idle", "running"}


def test_feedback_endpoint(gateway_client):
    r = gateway_client.post(
        "/feedback",
        json={
            "session_id": "s",
            "analysis_id": "a",
            "trace_id": "t-unknown",
            "sentiment": "positive",
        },
    )
    assert r.status_code == 200
