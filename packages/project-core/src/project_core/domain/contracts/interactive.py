from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ExecutionStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_INTERACTION = "awaiting_interaction"
    CANCEL_REQUESTED = "cancel_requested"
    RETRY_SCHEDULED = "retry_scheduled"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class InteractionKind(StrEnum):
    CLARIFICATION = "clarification"
    CONFIRMATION = "confirmation"
    ARTIFACT_REVIEW = "artifact_review"


class InteractionStatus(StrEnum):
    PENDING = "pending"
    ANSWERED = "answered"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class AnalysisEventType(StrEnum):
    QUEUED = "queued"
    STARTED = "started"
    PROGRESS = "progress"
    STAGE_COMPLETED = "stage_completed"
    AGENT_ACTION = "agent_action"
    INTERACTION_REQUESTED = "interaction_requested"
    INTERACTION_ANSWERED = "interaction_answered"
    RETRY_SCHEDULED = "retry_scheduled"
    ARTIFACT_CREATED = "artifact_created"
    WARNING = "warning"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCEL_REQUESTED = "cancel_requested"
    CANCELLED = "cancelled"


class SafeError(BaseModel):
    code: str
    message: str
    retryable: bool = False


class AnalysisJob(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    actor_id: str
    actor_role: str = ""
    tenant_id: str = ""
    store_ids: list[int] | None = None
    message: str
    status: ExecutionStatus = ExecutionStatus.QUEUED
    outcome: str | None = None
    revision: int = 1
    event_cursor: int = 0
    progress: float = 0.0
    current_stage: str | None = None
    parent_analysis_id: str | None = None
    legacy_analysis_id: str | None = None
    trace_id: str | None = None
    pending_interaction_id: str | None = None
    result_message: str | None = None
    safe_error: SafeError | None = None
    idempotency_key: str | None = None
    attempt: int = 0
    max_attempts: int = 3
    lease_owner: str | None = None
    lease_expires_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    updated_at: datetime = Field(default_factory=utc_now)


class AnalysisCheckpoint(BaseModel):
    analysis_id: str
    boundary: Literal["accepted", "ingress", "pipeline", "interaction", "terminal"]
    revision: int
    context: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class AnalysisEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    analysis_id: str
    sequence: int = 0
    event_type: AnalysisEventType
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class PendingInteraction(BaseModel):
    interaction_id: str = Field(default_factory=lambda: str(uuid4()))
    analysis_id: str
    actor_id: str
    kind: InteractionKind
    status: InteractionStatus = InteractionStatus.PENDING
    revision: int = 1
    prompt: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    response: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=utc_now)
    answered_at: datetime | None = None


class InteractionCommand(BaseModel):
    interaction_id: str
    expected_revision: int
    idempotency_key: str = Field(min_length=1, max_length=200)
    response: dict[str, Any] = Field(default_factory=dict)


class InteractionResult(BaseModel):
    interaction: PendingInteraction
    duplicate: bool = False


class SessionSummary(BaseModel):
    session_id: str
    actor_id: str
    tenant_id: str = ""
    title: str = ""
    archived: bool = False
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class TranscriptEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    analysis_id: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class AttachmentMetadata(BaseModel):
    attachment_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    actor_id: str
    file_name: str
    mime_type: str = ""
    byte_size: int = 0
    sha256: str = ""
    created_at: datetime = Field(default_factory=utc_now)


class ArtifactMetadata(BaseModel):
    artifact_id: str = Field(default_factory=lambda: str(uuid4()))
    analysis_id: str
    actor_id: str
    name: str
    media_type: str = "application/octet-stream"
    byte_size: int | None = None
    download_url: str | None = None
    review_status: Literal["pending", "approved", "rejected", "revision_requested"] = "pending"
    created_at: datetime = Field(default_factory=utc_now)


class Page(BaseModel):
    items: list[Any] = Field(default_factory=list)
    next_cursor: str | None = None

