#!/usr/bin/env python3
"""Post-deploy smoke test: login + one /chat round-trip."""

from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.config.env import load_project_env  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> int:
    load_project_env(ROOT)
    base = os.getenv("CHAT_GATEWAY_URL", "http://localhost:18300").rstrip("/")
    password = os.getenv("AUTH_SEED_HQ_ANALYST_PASSWORD", "")
    if not password:
        print("smoke: missing AUTH_SEED_HQ_ANALYST_PASSWORD in .env", file=sys.stderr)
        return 1
    with httpx.Client(timeout=600.0) as client:
        ready = client.get(f"{base}/health/ready")
        print("health/ready", ready.status_code, ready.json())
        login = client.post(
            f"{base}/auth/login",
            json={"username": "hq.analyst", "password": password},
        )
        print("login", login.status_code)
        if login.status_code != 200:
            print(login.text[:500], file=sys.stderr)
            return 1
        token = login.json()["access_token"]
        session_id = f"deploy-smoke-{uuid.uuid4().hex[:8]}"
        chat = client.post(
            f"{base}/chat",
            json={"session_id": session_id, "message": "Cho tôi doanh thu VIP tháng gần nhất"},
            headers={"Authorization": f"Bearer {token}"},
        )
        print("chat", chat.status_code)
        if chat.status_code != 200:
            print(chat.text[:800], file=sys.stderr)
            return 1
        body = chat.json()
        print(json.dumps({k: body.get(k) for k in ("outcome", "workflow_status", "message", "error")}, ensure_ascii=False))
        if body.get("error"):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
