from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from project_core.domain.contracts.feedback import FeedbackRecord

from chat_gateway.auth import current_user, issue_token
from chat_gateway.orchestrator import ChatOrchestrator

app = FastAPI(title="chat-gateway")
_orchestrator: ChatOrchestrator | None = None


def get_orchestrator() -> ChatOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ChatOrchestrator()
    return _orchestrator


class ChatRequest(BaseModel):
    session_id: str
    message: str


class FeedbackRequest(BaseModel):
    session_id: str
    analysis_id: str
    trace_id: str
    sentiment: str
    comment: str | None = None


class DevLoginRequest(BaseModel):
    actor_id: str = "dev-user"
    role: str = "hq_analyst"


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/auth/dev-login")
def dev_login(body: DevLoginRequest) -> dict[str, str]:
    if os.getenv("ALLOW_DEV_AUTH") != "1":
        raise HTTPException(status_code=403, detail="dev_auth_disabled")
    token = issue_token(body.actor_id, body.role)
    return {"access_token": token}


@app.get("/auth/login")
def oauth_login() -> dict[str, str]:
    from chat_gateway.oauth import oauth_provider_from_env

    provider = oauth_provider_from_env()
    state = "dev"
    return {"authorization_url": provider.authorization_url(state)}


@app.get("/auth/callback")
def oauth_callback(code: str) -> dict[str, Any]:
    from chat_gateway.oauth import oauth_provider_from_env

    return oauth_provider_from_env().exchange_code(code)


@app.post("/chat")
def chat(body: ChatRequest, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    os.environ.setdefault("ALLOW_LLM_STUB", "1")
    resp = get_orchestrator().handle_chat(session_id=body.session_id, message=body.message, user=user)
    return resp.model_dump()


@app.post("/feedback")
def feedback(body: FeedbackRequest, user: dict[str, Any] = Depends(current_user)) -> dict[str, str]:
    orch = get_orchestrator()
    if orch.feedback:
        record = FeedbackRecord(
            id=str(body.trace_id),
            trace_id=body.trace_id,
            analysis_id=body.analysis_id,
            session_id=body.session_id,
            actor_id=user["sub"],
            source="explicit",
            sentiment=body.sentiment,  # type: ignore[arg-type]
            confidence=1.0,
            evidence=body.comment or "",
        )
        orch.feedback.on_user_feedback(record)
    return {"status": "ok"}


@app.get("/analysis/{analysis_id}/status")
def analysis_status(analysis_id: str, user: dict[str, Any] = Depends(current_user)) -> dict[str, str]:
    return {"analysis_id": analysis_id, "status": "unknown"}


@app.get("/artifacts/{trace_id}/{file_name}")
def get_artifact(trace_id: str, file_name: str, user: dict[str, Any] = Depends(current_user)) -> FileResponse:
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        raise HTTPException(status_code=400, detail="invalid_path")
    base = Path(os.getenv("ARTIFACTS_DIR", "data/artifacts")) / trace_id / "out"
    path = base / file_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="not_found")
    return FileResponse(path)


def main() -> None:
    import uvicorn

    uvicorn.run("chat_gateway.app:app", host="0.0.0.0", port=int(os.getenv("CHAT_GATEWAY_PORT", "8300")))


if __name__ == "__main__":
    main()
