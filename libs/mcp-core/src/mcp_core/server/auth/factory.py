"""Build MCP authorizers from config."""

from __future__ import annotations

import os

from mcp_core.server.auth.base import (
    AllowAll,
    AuthContext,
    AuthPolicy,
    Authorizer,
    BearerTokenAuthorizer,
    CompositeAuthorizer,
    JwtAuthorizer,
)


def build_authorizer(
    *,
    mode: str = "none",
    token_env: str | None = None,
    jwt_secret_env: str | None = None,
    scopes: dict[str, list[str]] | None = None,
) -> Authorizer:
    mode = (mode or "none").lower()
    policy = AuthPolicy(tool_scopes=scopes or {})

    if mode in ("none", "allow_all"):
        return AllowAll()

    if mode == "bearer":
        token = os.getenv(token_env) if token_env else None
        if not token:
            raise ValueError(f"bearer auth requires env {token_env}")
        tokens = {
            token: AuthContext(principal="api-client", scopes=["*"], token=token),
        }
        return BearerTokenAuthorizer(tokens, policy=policy)

    if mode == "jwt":
        secret = os.getenv(jwt_secret_env or "MCP_JWT_SECRET")
        if not secret:
            raise ValueError("jwt auth requires MCP_JWT_SECRET or jwt_secret_env")
        return JwtAuthorizer(secret=secret, policy=policy)

    if mode == "composite":
        parts: list[Authorizer] = []
        if token_env and os.getenv(token_env):
            parts.append(build_authorizer(mode="bearer", token_env=token_env, scopes=scopes))
        if jwt_secret_env or os.getenv("MCP_JWT_SECRET"):
            parts.append(
                build_authorizer(mode="jwt", jwt_secret_env=jwt_secret_env, scopes=scopes)
            )
        if not parts:
            return AllowAll()
        return CompositeAuthorizer(parts, policy=policy)

    raise ValueError(f"Unknown auth mode: {mode}")
