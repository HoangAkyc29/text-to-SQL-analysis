from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class FeedbackRecord(BaseModel):
    feedback_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    trace_id: str | None = None
    actor_id: str
    sentiment: str
    confidence: float = 1.0
    comment: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BehavioralSignal(BaseModel):
    signal_type: str
    session_id: str
    trace_id: str | None = None
    weight: float = 0.5
    metadata: dict[str, Any] = Field(default_factory=dict)
