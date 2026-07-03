"""Circuit breaker on HTTP clients."""

from __future__ import annotations

import pytest

from project_core.domain.errors.codes import AgentUnavailableError
from project_core.infra.resilience import CircuitBreaker

pytestmark = pytest.mark.unit


def test_circuit_opens_after_failures():
    cb = CircuitBreaker(failure_threshold=3, open_seconds=60)
    for _ in range(3):
        cb.record_failure()
    assert cb.is_open()


def test_http_sql_gateway_fast_fail_when_open(monkeypatch):
    from chat_gateway.clients import HttpSqlGatewayClient
    from project_core.domain.contracts.sql_acl import SqlAclContext

    client = HttpSqlGatewayClient()
    for _ in range(5):
        client._circuit.record_failure()
    acl = SqlAclContext(actor_id="u", allowed_tables=["STRANS"])
    with pytest.raises(AgentUnavailableError):
        client.validate_sql("SELECT 1", acl)
