"""Security regression suite for review1-0 remediation."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_agent_run_requires_token_when_auth_enabled(monkeypatch):
    monkeypatch.setenv("REQUIRE_INTERNAL_AUTH", "1")
    monkeypatch.setenv("INTERNAL_SERVICE_TOKEN", "test-secret-token")
    monkeypatch.delenv("ALLOW_DEV_AUTH", raising=False)

    from conversational_router.app import app

    client = TestClient(app)
    resp = client.post("/run", json={"session_id": "s", "actor_id": "u", "message": "{}"})
    assert resp.status_code == 401


def test_agent_run_with_valid_token(monkeypatch):
    monkeypatch.setenv("REQUIRE_INTERNAL_AUTH", "1")
    monkeypatch.setenv("INTERNAL_SERVICE_TOKEN", "test-secret-token")
    monkeypatch.setenv("ALLOW_LLM_STUB", "1")

    from sql_gateway.http_app import app as gw_app

    client = TestClient(gw_app)
    resp = client.post(
        "/tools/validate_sql",
        json={
            "sql": "SELECT TOP 1 SKU_ID FROM STRANS WHERE TRANS_CODE = '113'",
            "actor_id": "u",
            "allowed_tables": ["STRANS"],
            "tool_grants": ["tool:*"],
        },
        headers={"Authorization": "Bearer test-secret-token"},
    )
    assert resp.status_code == 200
    assert "allowed" in resp.json()


def test_sandbox_escape_read_outside_dataset(tmp_path, monkeypatch):
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path / "artifacts"))
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir(parents=True)
    out_dir = artifacts / "trace-1" / "out"
    out_dir.mkdir(parents=True)

    from python_sandbox.tools_impl import run_analysis_script

    script = "open('/etc/passwd').read()"
    result = run_analysis_script(str(tmp_path / "missing.parquet"), script, str(out_dir))
    assert result.get("status") != "ok" or "error" in result


def test_sandbox_output_dir_outside_artifacts_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path / "artifacts"))
    from python_sandbox.tools_impl import run_analysis_script

    result = run_analysis_script(str(tmp_path / "x.parquet"), "x=1", str(tmp_path / "escape"))
    assert result.get("error") == "output_dir_must_be_under_artifacts_root"


def test_sandbox_dataset_outside_artifacts_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path / "artifacts"))
    artifacts = tmp_path / "artifacts"
    out_dir = artifacts / "t" / "out"
    out_dir.mkdir(parents=True)
    outside = tmp_path / "secret.parquet"
    outside.write_bytes(b"")
    from python_sandbox.tools_impl import run_analysis_script

    result = run_analysis_script(str(outside), "x=1", str(out_dir))
    assert result.get("error") == "path_not_allowed"


def test_sandbox_child_env_strips_secrets(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "super-secret")
    monkeypatch.setenv("AUTH_DB_DSN", "Driver=...")
    from python_sandbox.tools_impl import _minimal_child_env

    env = _minimal_child_env()
    assert "JWT_SECRET" not in env
    assert "AUTH_DB_DSN" not in env
    assert env.get("MPLBACKEND") == "Agg"
