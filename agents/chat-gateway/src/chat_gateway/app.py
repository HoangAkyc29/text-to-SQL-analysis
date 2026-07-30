from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import re
import time
from typing import Any
from uuid import uuid4

import httpx
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from project_core.config.env import load_project_env
from project_core.domain.contracts.clarification import ClarificationReply
from project_core.domain.contracts.feedback import DomainRuleCandidate, FeedbackRecord
from project_core.domain.contracts.interactive import (
    AnalysisEventType,
    AnalysisJob,
    AttachmentMetadata,
    ExecutionStatus,
    InteractionCommand,
    SessionSummary,
)
from project_core.domain.contracts.pipeline import ChatResponse
from project_core.domain.errors.codes import AgentUnavailableError, PermissionsUnavailableError
from project_core.ingest.attachments import ingest_file
from project_core.infra.analysis_repository import RepositoryConflict, RepositoryNotFound
from project_core.infra.live_trial_recorder import export_trial_bundle

from chat_gateway.analysis_service import AnalysisService, create_analysis_service
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
_analysis_service: AnalysisService | None = None


def get_orchestrator() -> ChatOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ChatOrchestrator()
    return _orchestrator


def get_analysis_service() -> AnalysisService:
    global _analysis_service
    if _analysis_service is None:
        try:
            _analysis_service = create_analysis_service()
        except Exception as exc:
            raise HTTPException(
                status_code=503, detail="durable_analysis_store_unavailable"
            ) from exc
    return _analysis_service


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


class AnalysisSubmitRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=20_000)


class RephraseRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20_000)


class SessionCreateRequest(BaseModel):
    session_id: str | None = None
    title: str = Field(default="", max_length=200)


class SessionUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    archived: bool | None = None


class ArtifactReviewRequest(BaseModel):
    action: str
    comment: str | None = Field(default=None, max_length=2_000)


def _job_response(job: AnalysisJob) -> dict[str, Any]:
    return {
        "analysis_id": job.analysis_id,
        "session_id": job.session_id,
        "status": job.status.value,
        "outcome": job.outcome,
        "revision": job.revision,
        "event_cursor": job.event_cursor,
        "progress": job.progress,
        "current_stage": job.current_stage,
        "parent_analysis_id": job.parent_analysis_id,
        "pending_interaction_id": job.pending_interaction_id,
        "legacy_analysis_id": job.legacy_analysis_id,
        "trace_id": job.trace_id,
        "result_message": job.result_message,
        "error": job.safe_error.model_dump(mode="json") if job.safe_error else None,
        "created_at": job.created_at.isoformat(),
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "updated_at": job.updated_at.isoformat(),
    }


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


@app.get("/auth/me")
def auth_me(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return {
        "actor_id": str(user["sub"]),
        "role": str(user.get("role") or ""),
        "tenant_id": str(user.get("tenant_id") or ""),
        "store_ids": user.get("store_ids"),
        "expires_at": user.get("exp"),
    }


@app.post("/analyses", status_code=202)
def submit_analysis(
    body: AnalysisSubmitRequest,
    request: Request,
    user: dict[str, Any] = Depends(current_user),
) -> JSONResponse:
    job, created = get_analysis_service().submit(
        session_id=body.session_id,
        message=body.message,
        user=user,
        idempotency_key=request.headers.get("Idempotency-Key"),
    )
    return JSONResponse(
        status_code=202 if created else 200,
        content={**_job_response(job), "created": created},
    )


@app.get("/analyses/{analysis_id}")
def get_analysis(
    analysis_id: str, user: dict[str, Any] = Depends(current_user)
) -> dict[str, Any]:
    job = get_analysis_service().get_job(analysis_id, str(user["sub"]))
    if job is None:
        raise HTTPException(status_code=404, detail="analysis_not_found")
    result = _job_response(job)
    result["artifacts"] = [
        {
            **item.model_dump(mode="json"),
            "url": item.download_url,
            "file_name": item.name,
        }
        for item in get_analysis_service().repository.list_artifacts(
            analysis_id, str(user["sub"])
        )
    ]
    pending = None
    if job.pending_interaction_id:
        pending = get_analysis_service().repository.get_interaction(
            job.pending_interaction_id
        )
    result["pending_interaction"] = (
        pending.model_dump(mode="json") if pending is not None else None
    )
    return result


@app.get("/analyses/{analysis_id}/events")
async def analysis_events(
    analysis_id: str,
    request: Request,
    after: int = 0,
    user: dict[str, Any] = Depends(current_user),
) -> StreamingResponse:
    service = get_analysis_service()
    actor_id = str(user["sub"])
    if service.get_job(analysis_id, actor_id) is None:
        raise HTTPException(status_code=404, detail="analysis_not_found")
    raw_last_id = request.headers.get("Last-Event-ID")
    if raw_last_id:
        try:
            after = max(after, int(raw_last_id))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="invalid_last_event_id") from exc

    async def stream() -> Any:
        cursor = after
        last_heartbeat = time.monotonic()
        while True:
            if await request.is_disconnected():
                return
            events = service.repository.list_events(analysis_id, after=cursor, limit=200)
            for event in events:
                cursor = event.sequence
                payload = event.model_dump_json()
                yield f"id: {event.sequence}\nevent: {event.event_type.value}\ndata: {payload}\n\n"
            job = service.get_job(analysis_id, actor_id)
            if job is None:
                return
            terminal = job.status in {
                ExecutionStatus.SUCCEEDED,
                ExecutionStatus.FAILED,
                ExecutionStatus.CANCELLED,
                ExecutionStatus.EXPIRED,
            }
            if terminal and cursor >= job.event_cursor:
                return
            now = time.monotonic()
            if now - last_heartbeat >= int(os.getenv("SSE_HEARTBEAT_SECONDS", "15")):
                yield ": heartbeat\n\n"
                last_heartbeat = now
            await asyncio.sleep(0.5)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/analyses/{analysis_id}/trial-log")
def get_analysis_trial_log(
    analysis_id: str, user: dict[str, Any] = Depends(current_user)
) -> dict[str, Any]:
    """Evaluation bundle: Mongo events + JSONL mirror + interactions/artifacts/audit."""
    service = get_analysis_service()
    actor_id = str(user["sub"])
    try:
        return export_trial_bundle(
            analysis_id=analysis_id,
            repository=service.repository,
            actor_id=actor_id,
            recorder=service.recorder,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="analysis_not_found") from exc


@app.get("/analyses/{analysis_id}/interactions")
def list_interactions(
    analysis_id: str, user: dict[str, Any] = Depends(current_user)
) -> list[dict[str, Any]]:
    service = get_analysis_service()
    actor_id = str(user["sub"])
    if service.get_job(analysis_id, actor_id) is None:
        raise HTTPException(status_code=404, detail="analysis_not_found")
    return [
        item.model_dump(mode="json")
        for item in service.repository.list_interactions(analysis_id, actor_id)
    ]


@app.post("/analyses/{analysis_id}/interactions")
def answer_analysis_interaction(
    analysis_id: str,
    body: InteractionCommand,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    try:
        result = get_analysis_service().answer_interaction(
            analysis_id, str(user["sub"]), body
        )
        return result.model_dump(mode="json")
    except RepositoryNotFound as exc:
        raise HTTPException(status_code=404, detail="interaction_not_found") from exc
    except RepositoryConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/analyses/{analysis_id}/cancel", status_code=202)
def cancel_analysis(
    analysis_id: str, user: dict[str, Any] = Depends(current_user)
) -> dict[str, Any]:
    try:
        return _job_response(
            get_analysis_service().cancel(analysis_id, str(user["sub"]))
        )
    except RepositoryNotFound as exc:
        raise HTTPException(status_code=404, detail="analysis_not_found") from exc


@app.post("/analyses/{analysis_id}/rephrase", status_code=202)
def rephrase_analysis(
    analysis_id: str,
    body: RephraseRequest,
    request: Request,
    user: dict[str, Any] = Depends(current_user),
) -> JSONResponse:
    try:
        job, created = get_analysis_service().rephrase(
            analysis_id,
            str(user["sub"]),
            body.message,
            user,
            request.headers.get("Idempotency-Key"),
        )
    except RepositoryNotFound as exc:
        raise HTTPException(status_code=404, detail="analysis_not_found") from exc
    return JSONResponse(
        status_code=202 if created else 200,
        content={**_job_response(job), "created": created},
    )


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


@app.post("/sessions", status_code=201)
def create_session(
    body: SessionCreateRequest,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    session = SessionSummary(
        session_id=body.session_id or str(uuid4()),
        actor_id=str(user["sub"]),
        tenant_id=str(user.get("tenant_id") or ""),
        title=body.title,
    )
    existing = get_analysis_service().repository.get_session(
        session.session_id, session.actor_id
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="session_exists")
    return get_analysis_service().repository.ensure_session(session).model_dump(
        mode="json"
    )


@app.get("/sessions")
def list_sessions(
    limit: int = 50, user: dict[str, Any] = Depends(current_user)
) -> dict[str, Any]:
    items = get_analysis_service().repository.list_sessions(
        str(user["sub"]), min(max(limit, 1), 200)
    )
    return {"items": [item.model_dump(mode="json") for item in items], "next_cursor": None}


@app.get("/sessions/{session_id}")
def get_session(
    session_id: str, user: dict[str, Any] = Depends(current_user)
) -> dict[str, Any]:
    item = get_analysis_service().repository.get_session(
        session_id, str(user["sub"])
    )
    if item is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    return item.model_dump(mode="json")


@app.patch("/sessions/{session_id}")
def update_session(
    session_id: str,
    body: SessionUpdateRequest,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    item = get_analysis_service().repository.update_session(
        session_id,
        str(user["sub"]),
        body.model_dump(exclude_none=True),
    )
    if item is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    return item.model_dump(mode="json")


@app.get("/sessions/{session_id}/transcript")
def get_transcript(
    session_id: str,
    limit: int = 500,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    service = get_analysis_service()
    if service.repository.get_session(session_id, str(user["sub"])) is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    items = service.repository.list_transcript(
        session_id, str(user["sub"]), min(max(limit, 1), 1000)
    )
    return {"items": [item.model_dump(mode="json") for item in items], "next_cursor": None}


@app.post("/attachments")
async def upload_attachment(
    session_id: str,
    file: UploadFile = File(...),
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    durable_service: AnalysisService | None = None
    try:
        durable_service = get_analysis_service()
        owned_session = durable_service.repository.ensure_session(
            SessionSummary(
                session_id=session_id,
                actor_id=str(user["sub"]),
                tenant_id=str(user.get("tenant_id") or ""),
            )
        )
        if owned_session.actor_id != str(user["sub"]):
            raise HTTPException(status_code=403, detail="forbidden")
    except HTTPException as exc:
        if exc.status_code != 503:
            raise
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="file_too_large")
    source = ingest_file(
        session_id=session_id,
        file_name=file.filename or "upload.bin",
        content=content,
    )
    get_orchestrator().attach_external_sources(session_id, [source.model_dump()])
    metadata = AttachmentMetadata(
        attachment_id=source.file_id,
        session_id=session_id,
        actor_id=str(user["sub"]),
        file_name=source.original_name or file.filename or "upload.bin",
        mime_type=source.mime,
        byte_size=source.byte_size,
        sha256=source.sha256,
    )
    if durable_service is not None:
        durable_service.repository.add_attachment(metadata, source.model_dump())
    public_metadata = metadata.model_dump(mode="json")
    return {
        "status": "ok",
        "attachment": public_metadata,
        "source": {
            "file_id": metadata.attachment_id,
            "mime": metadata.mime_type,
            "original_name": metadata.file_name,
            "byte_size": metadata.byte_size,
            "sha256": metadata.sha256,
        },
    }


@app.get("/sessions/{session_id}/attachments")
def list_attachments(
    session_id: str, user: dict[str, Any] = Depends(current_user)
) -> dict[str, Any]:
    service = get_analysis_service()
    if service.repository.get_session(session_id, str(user["sub"])) is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    items = service.repository.list_attachments(session_id, str(user["sub"]))
    return {"items": [item.model_dump(mode="json") for item in items], "next_cursor": None}


@app.delete("/attachments/{attachment_id}", status_code=204)
def delete_attachment(
    attachment_id: str, user: dict[str, Any] = Depends(current_user)
) -> None:
    if not get_analysis_service().repository.delete_attachment(
        attachment_id, str(user["sub"])
    ):
        raise HTTPException(status_code=404, detail="attachment_not_found")


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


@app.get("/domain-rules/page")
def list_domain_rules_page(
    status: str | None = None,
    limit: int = 50,
    cursor: str | None = None,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    if status not in {None, "candidate", "confirmed", "rejected"}:
        raise HTTPException(status_code=400, detail="invalid_domain_rule_status")
    try:
        offset = int(cursor or "0")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid_cursor") from exc
    page_size = min(max(limit, 1), 200)
    records = get_orchestrator().list_domain_rules(
        user=user,
        status=status,
        limit=page_size + 1,
        offset=max(offset, 0),
    )
    has_more = len(records) > page_size
    return {
        "items": records[:page_size],
        "next_cursor": str(max(offset, 0) + page_size) if has_more else None,
    }


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


@app.get("/analyses/{analysis_id}/artifacts")
def list_analysis_artifacts(
    analysis_id: str, user: dict[str, Any] = Depends(current_user)
) -> dict[str, Any]:
    service = get_analysis_service()
    actor_id = str(user["sub"])
    if service.get_job(analysis_id, actor_id) is None:
        raise HTTPException(status_code=404, detail="analysis_not_found")
    items = service.repository.list_artifacts(analysis_id, actor_id)
    return {"items": [item.model_dump(mode="json") for item in items], "next_cursor": None}


@app.post("/analyses/{analysis_id}/artifacts/{artifact_id}/review")
def review_analysis_artifact(
    analysis_id: str,
    artifact_id: str,
    body: ArtifactReviewRequest,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    if body.action not in {"approve", "reject", "request_revision"}:
        raise HTTPException(status_code=400, detail="invalid_artifact_review_action")
    service = get_analysis_service()
    actor_id = str(user["sub"])
    if service.get_job(analysis_id, actor_id) is None:
        raise HTTPException(status_code=404, detail="analysis_not_found")
    item = service.repository.review_artifact(
        artifact_id, analysis_id, actor_id, body.action
    )
    if item is None:
        raise HTTPException(status_code=404, detail="artifact_not_found")
    review_payload = {
        "kind": "artifact_review",
        "artifact_id": artifact_id,
        "action": body.action,
    }
    service.repository.append_event(
        analysis_id,
        AnalysisEventType.INTERACTION_ANSWERED,
        review_payload,
    )
    try:
        service.recorder.append(
            analysis_id,
            AnalysisEventType.INTERACTION_ANSWERED.value,
            review_payload,
            source="user",
        )
    except Exception:
        pass
    return item.model_dump(mode="json")


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
    return FileResponse(path, filename=resolved_name, content_disposition_type="attachment")


def main() -> None:
    import uvicorn

    uvicorn.run("chat_gateway.app:app", host="0.0.0.0", port=int(os.getenv("CHAT_GATEWAY_PORT", "18300")))


if __name__ == "__main__":
    main()
