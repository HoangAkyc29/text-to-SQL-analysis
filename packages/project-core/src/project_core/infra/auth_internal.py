from __future__ import annotations

import os

from fastapi import Header, HTTPException


def internal_auth_required() -> bool:
    if os.getenv("REQUIRE_INTERNAL_AUTH") == "1":
        return True
    token = os.getenv("INTERNAL_SERVICE_TOKEN", "").strip()
    return bool(token) and os.getenv("ALLOW_DEV_AUTH") != "1"


def verify_internal_service(
    authorization: str | None = Header(default=None),
    x_service_token: str | None = Header(default=None, alias="X-Service-Token"),
) -> None:
    if not internal_auth_required():
        return
    expected = os.getenv("INTERNAL_SERVICE_TOKEN", "").strip()
    if not expected:
        raise HTTPException(status_code=500, detail="internal_service_token_not_configured")
    token = x_service_token
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    if token != expected:
        raise HTTPException(status_code=401, detail="invalid_service_token")


def internal_auth_headers() -> dict[str, str]:
    token = os.getenv("INTERNAL_SERVICE_TOKEN", "").strip()
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}", "X-Service-Token": token}
