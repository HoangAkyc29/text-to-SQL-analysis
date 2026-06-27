from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from project_core.domain.contracts.clarification import ClarificationReply
from project_core.domain.contracts.workflow import ClarificationState, WorkflowState


class TranscriptTurn(BaseModel):
    id: str
    role: str
    content: str
    at: str
    analysis_id: str | None = None
    trace_id: str | None = None
    kind: str = "chat"
    artifact_urls: list[str] = Field(default_factory=list)


class SessionBundle(BaseModel):
    session_id: str
    actor_id: str
    transcript: list[TranscriptTurn] = Field(default_factory=list)
    workflow: WorkflowState | None = None
    clarification: ClarificationState | None = None
    permissions: Any | None = None
