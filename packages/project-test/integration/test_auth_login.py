"""Username/password login and permission claims."""

from __future__ import annotations

import pytest

from chat_gateway.auth_store import AuthUser, hash_password, verify_password
from project_core.domain.access.acl import build_permissions_snapshot
from project_core.domain.access.user_claims import claims_from_user_dict, normalize_store_ids
from project_core.domain.contracts.sql_acl import SqlAclContext

pytestmark = pytest.mark.unit


def test_normalize_store_ids_from_csv():
    assert normalize_store_ids("10001,10004") == [10001, 10004]
    assert normalize_store_ids([1, 2]) == [1, 2]
    assert normalize_store_ids(None) is None


def test_claims_from_user_dict():
    actor, role, stores = claims_from_user_dict(
        {"sub": "u1", "role": "store_manager", "store_ids": "10001,10004"}
    )
    assert actor == "u1"
    assert role == "store_manager"
    assert stores == [10001, 10004]


def test_bcrypt_roundtrip():
    hashed = hash_password("secret-pass")
    assert verify_password("secret-pass", hashed)
    assert not verify_password("wrong", hashed)


def test_store_manager_sql_acl_blocks_sensitive_column():
    from sql_gateway.tools_impl import execute_readonly

    perms = build_permissions_snapshot("mgr", "store_manager", store_ids=[10001])
    acl = SqlAclContext.from_permissions(perms)
    result = execute_readonly("SELECT TOP 1 SPPRICE FROM HISRTPR", acl=acl)
    assert result.get("error") == "policy_blocked" or result.get("violations")


def test_password_login_endpoint(monkeypatch, fake_redis):
    monkeypatch.delenv("ALLOW_DEV_AUTH", raising=False)
    monkeypatch.setenv("REQUIRE_INTERNAL_AUTH", "0")
    monkeypatch.setenv(
        "MONGODB_URI",
        "mongodb://127.0.0.1:65530/supermarket_agent?serverSelectionTimeoutMS=200",
    )

    def _fake_auth(username: str, password: str) -> AuthUser | None:
        if username == "hq.analyst" and password == "ok":
            return AuthUser(
                user_id="22222222-2222-2222-2222-222222222222",
                username=username,
                role="hq_analyst",
                store_ids=None,
                display_name="HQ",
                email="a@b.c",
            )
        return None

    monkeypatch.setattr("chat_gateway.auth_store.authenticate", _fake_auth)

    from fastapi.testclient import TestClient

    from chat_gateway.app import app

    client = TestClient(app)
    bad = client.post("/auth/login", json={"username": "hq.analyst", "password": "nope"})
    assert bad.status_code == 401

    ok = client.post("/auth/login", json={"username": "hq.analyst", "password": "ok"})
    assert ok.status_code == 200
    body = ok.json()
    assert body["access_token"]
    assert body["role"] == "hq_analyst"

    assert client.post("/chat", json={"session_id": "auth-sess", "message": "hi"}).status_code == 401
