from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any

import httpx
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from project_core.config.env import load_project_env
from project_core.domain.contracts.clarification import ClarificationReply
from project_core.domain.contracts.feedback import DomainRuleCandidate, FeedbackRecord
from project_core.domain.contracts.pipeline import ChatResponse
from project_core.domain.errors.codes import AgentUnavailableError, PermissionsUnavailableError
from project_core.ingest.attachments import ingest_file

from chat_gateway.auth import current_user, issue_token
from chat_gateway.orchestrator import ChatOrchestrator

load_project_env()

app = FastAPI(title="chat-gateway")


@app.exception_handler(PermissionsUnavailableError)
async def _permissions_unavailable_handler(
    _request: Request, exc: PermissionsUnavailableError
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"detail": "permissions_unavailable", "code": exc.code},
    )
_orchestrator: ChatOrchestrator | None = None


def get_orchestrator() -> ChatOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ChatOrchestrator()
    return _orchestrator


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ClarifyRequest(BaseModel):
    session_id: str
    reply: ClarificationReply


class FeedbackRequest(BaseModel):
    session_id: str
    analysis_id: str
    trace_id: str
    sentiment: str
    comment: str | None = None


class DomainRuleConfirmRequest(BaseModel):
    rule_id: str
    confirmed: bool = True


class DomainRuleStageRequest(BaseModel):
    trace_id: str
    candidate: DomainRuleCandidate


class DomainRuleReviewRequest(BaseModel):
    action: str


class DevLoginRequest(BaseModel):
    actor_id: str = "dev-user"
    role: str = "hq_analyst"


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/health")
def health() -> dict:
    return {"ok": True, "redis": True, "mongo": get_orchestrator().feedback is not None, "agents": {}}


@app.get("/health/live")
def health_live() -> dict[str, bool]:
    return {"ok": True}


@app.get("/health/ready")
def health_ready() -> dict:
    import httpx

    orch = get_orchestrator()
    agents: dict[str, str] = {}
    for key, url in orch.pipeline.agent_invoker.urls.items():  # type: ignore[attr-defined]
        try:
            resp = httpx.get(f"{url}/health", timeout=2.0)
            agents[key] = "ok" if resp.status_code == 200 else "error"
        except Exception:
            agents[key] = "error"
    redis_ok = True
    try:
        orch.stm.client.ping()  # type: ignore[attr-defined]
    except Exception:
        redis_ok = False
    mongo_ok = orch.feedback is not None
    return {"ok": redis_ok and mongo_ok, "redis": redis_ok, "mongo": mongo_ok, "agents": agents}


@app.post("/auth/dev-login")
def dev_login(body: DevLoginRequest) -> dict[str, str]:
    if os.getenv("ALLOW_DEV_AUTH") != "1":
        raise HTTPException(status_code=403, detail="dev_auth_disabled")
    token = issue_token(body.actor_id, body.role)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/auth/login")
def login(body: LoginRequest) -> dict[str, str]:
    from chat_gateway.auth_store import authenticate

    user = authenticate(body.username, body.password)
    if user is None:
        raise HTTPException(status_code=401, detail="invalid_credentials")
    token = issue_token(user.user_id, user.role, user.store_ids)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "display_name": user.display_name,
    }


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
    try:
        resp = get_orchestrator().handle_chat(session_id=body.session_id, message=body.message, user=user)
    except (httpx.ReadTimeout, httpx.HTTPError, AgentUnavailableError) as exc:
        resp = ChatResponse(
            session_id=body.session_id,
            workflow_status="error",
            message="Hệ thống đang xử lý chậm, vui lòng thử lại sau.",
            error={"code": "AGENT_TIMEOUT", "retryable": True, "detail": str(exc)},
        )
    return resp.model_dump()


@app.post("/chat/clarify")
def chat_clarify(body: ClarifyRequest, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    resp = get_orchestrator().handle_clarify(session_id=body.session_id, reply=body.reply, user=user)
    return resp.model_dump()


@app.post("/attachments")
async def upload_attachment(
    session_id: str,
    file: UploadFile = File(...),
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="file_too_large")
    source = ingest_file(
        session_id=session_id,
        file_name=file.filename or "upload.bin",
        content=content,
    )
    get_orchestrator().attach_external_sources(session_id, [source.model_dump()])
    return {"status": "ok", "source": source.model_dump()}


@app.post("/domain-rules/confirm")
def confirm_domain_rule(
    body: DomainRuleConfirmRequest,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, str]:
    try:
        return get_orchestrator().confirm_domain_rule(body.rule_id, confirmed=body.confirmed, user=user)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="domain_rule_not_found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail="domain_rule_review_forbidden") from exc


@app.post("/domain-rules/candidates")
def stage_domain_rule(
    body: DomainRuleStageRequest,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, str]:
    return get_orchestrator().stage_domain_rule(body.candidate, trace_id=body.trace_id, user=user)


@app.get("/domain-rules")
def list_domain_rules(
    status: str | None = None,
    limit: int = 50,
    user: dict[str, Any] = Depends(current_user),
) -> list[dict[str, Any]]:
    if status not in {None, "candidate", "confirmed", "rejected"}:
        raise HTTPException(status_code=400, detail="invalid_domain_rule_status")
    return get_orchestrator().list_domain_rules(
        user=user,
        status=status,
        limit=min(max(limit, 1), 200),
    )


@app.post("/domain-rules/{rule_id}/review")
def review_domain_rule(
    rule_id: str,
    body: DomainRuleReviewRequest,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, str]:
    if body.action not in {"confirm", "reject", "stale"}:
        raise HTTPException(status_code=400, detail="invalid_domain_rule_review_action")
    try:
        return get_orchestrator().review_domain_rule(rule_id, action=body.action, user=user)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="domain_rule_not_found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail="domain_rule_review_forbidden") from exc


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
        if body.sentiment == "positive" and orch.analysis_tool_registry:
            tool = orch.analysis_tool_registry.find_by_trace(body.trace_id)
            if tool:
                orch.analysis_tool_registry.promote(tool["tool_id"])
    return {"status": "ok"}


@app.get("/analysis/{analysis_id}/status")
def analysis_status(analysis_id: str, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    result = get_orchestrator().analysis_status(analysis_id, actor_id=str(user["sub"]))
    if result.get("status") == "forbidden":
        raise HTTPException(status_code=403, detail="forbidden")
    return result


@app.get("/artifacts/{trace_id}/{file_name}")
def get_artifact(
    trace_id: str,
    file_name: str,
    session_id: str | None = None,
    user: dict[str, Any] = Depends(current_user),
) -> FileResponse:
    if (
        not re.fullmatch(r"[A-Za-z0-9-]{16,64}", trace_id)
        or ".." in file_name
        or "/" in file_name
        or "\\" in file_name
        or Path(file_name).name != file_name
    ):
        raise HTTPException(status_code=400, detail="invalid_path")
    root = Path(os.getenv("ARTIFACTS_DIR", "data/artifacts")).resolve()
    trace_root = (root / trace_id).resolve()
    try:
        trace_root.relative_to(root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid_path") from exc
    owner_path = trace_root / "owner.json"
    if not owner_path.exists():
        raise HTTPException(status_code=403, detail="trace_owner_unknown")
    try:
        owner = json.loads(owner_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=403, detail="trace_owner_invalid") from exc
    if str(owner.get("actor_id")) != str(user["sub"]):
        raise HTTPException(status_code=403, detail="forbidden")
    base = (trace_root / "out").resolve()
    resolved_name = file_name
    artifact_manifest = trace_root / "artifact_manifest.json"
    if artifact_manifest.exists():
        try:
            records = json.loads(artifact_manifest.read_text(encoding="utf-8"))
            match = next(
                (
                    item
                    for item in records
                    if str(item.get("artifact_id")) == file_name
                ),
                None,
            )
            if match:
                resolved_name = Path(str(match.get("path") or "")).name
        except Exception:
            pass
    path = (base / resolved_name).resolve()
    try:
        path.relative_to(base)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid_path") from exc
    if not path.exists() or not path.is_file() or path.is_symlink():
        raise HTTPException(status_code=404, detail="not_found")
    if session_id:
        get_orchestrator().record_artifact_download(session_id, trace_id)
    return FileResponse(path)


def main() -> None:
    import uvicorn

    uvicorn.run("chat_gateway.app:app", host="0.0.0.0", port=int(os.getenv("CHAT_GATEWAY_PORT", "18300")))


if __name__ == "__main__":
    main()
