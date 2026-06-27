from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer(auto_error=False)
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALG = "HS256"


def issue_token(actor_id: str, role: str, store_ids: list[int] | None = None) -> str:
    payload = {
        "sub": actor_id,
        "role": role,
        "store_ids": store_ids,
        "exp": datetime.utcnow() + timedelta(hours=8),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="invalid_token") from exc


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict[str, Any]:
    if credentials is None:
        if os.getenv("ALLOW_DEV_AUTH") == "1":
            return {"sub": "dev-user", "role": "hq_analyst", "store_ids": None}
        raise HTTPException(status_code=401, detail="missing_token")
    return decode_token(credentials.credentials)
