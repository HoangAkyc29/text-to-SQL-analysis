"""Opt-in live SQL tests."""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.live


@pytest.mark.skipif(not os.getenv("ANALYTICS_DB_DSN"), reason="ANALYTICS_DB_DSN not set")
def test_live_sql_gateway_health():
    from sql_gateway.app import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
