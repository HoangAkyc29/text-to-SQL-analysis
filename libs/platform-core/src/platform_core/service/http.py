"""Optional FastAPI inbound helper for A2A ``/run`` endpoints."""

from __future__ import annotations

import os
from typing import Any, Callable

from agent_core.io.schemas import AgentRequest, AgentResponse


def create_a2a_app(
    run_handler: Callable[[AgentRequest], AgentResponse],
    *,
    token_env: str | None = None,
) -> Any:
    """Create a minimal FastAPI app exposing ``POST /run``.

    Requires platform-core[fastapi]. When *token_env* is set, requests must
  carry a matching ``Authorization: Bearer`` header.
    """
    try:
        from fastapi import Depends, FastAPI, Header, HTTPException
    except ImportError as exc:
        raise ImportError("create_a2a_app requires platform-core[fastapi]") from exc

    app = FastAPI(title="Agent A2A")

    def _auth(authorization: str | None = Header(default=None)) -> None:
        if not token_env:
            return
        expected = os.getenv(token_env)
        if not expected:
            return
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="missing bearer token")
        if authorization[7:].strip() != expected:
            raise HTTPException(status_code=403, detail="invalid bearer token")

    @app.post("/run", response_model=AgentResponse)
    def run_agent(request: AgentRequest, _auth: None = Depends(_auth)) -> AgentResponse:
        return run_handler(request)

    return app
