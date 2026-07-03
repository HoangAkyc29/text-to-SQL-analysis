from __future__ import annotations

import logging
import os
from datetime import timedelta

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from project_core.domain.time import utc_now

logger = logging.getLogger(__name__)
_bearer = HTTPBearer(auto_error=False)
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALG = "HS256"
_WEAK_SECRETS = frozenset({"change-me-in-production", "changeme", "secret", "dev"})


def _validate_jwt_secret_at_startup() -> None:
    if os.getenv("REQUIRE_PROD_AUTH") == "1":
        if not JWT_SECRET or JWT_SECRET.lower() in _WEAK_SECRETS or len(JWT_SECRET) < 32:
            raise RuntimeError("JWT_SECRET too weak for production — set REQUIRE_PROD_AUTH=0 for dev only")
    elif JWT_SECRET.lower() in _WEAK_SECRETS:
        logger.warning("JWT_SECRET is default — do not use in production")


_validate_jwt_secret_at_startup()


def issue_token(actor_id: str, role: str, store_ids: list[int] | None = None) -> str:
    payload = {
        "sub": actor_id,
        "role": role,
        "store_ids": store_ids,
        "exp": utc_now() + timedelta(hours=8),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="invalid_token") from exc


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    if credentials is None:
        if os.getenv("ALLOW_DEV_AUTH") == "1":
            return {"sub": "dev-user", "role": "hq_analyst", "store_ids": None}
        raise HTTPException(status_code=401, detail="missing_token")
    return decode_token(credentials.credentials)
