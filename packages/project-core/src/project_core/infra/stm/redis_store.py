from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any
from uuid import uuid4

import redis
from pydantic import BaseModel

from project_core.config.loader import load_project_config
from project_core.domain.contracts.workflow import WorkflowState
from project_core.domain.memory.session_bundle import SessionBundle, TranscriptTurn


class RedisSessionStore:
    def __init__(self, url: str | None = None, *, ttl_days: int | None = None) -> None:
        cfg = load_project_config()
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.ttl_seconds = int((ttl_days or cfg.stm.session_ttl_days) * 86400)
        self.client = redis.from_url(self.url, decode_responses=True)

    def _key(self, session_id: str, suffix: str) -> str:
        return f"stm:{session_id}:{suffix}"

    def load_session(self, session_id: str) -> SessionBundle:
        transcript_raw = self.client.get(self._key(session_id, "transcript"))
        workflow_raw = self.client.get(self._key(session_id, "workflow"))
        clarification_raw = self.client.get(self._key(session_id, "clarification"))
        transcript = []
        if transcript_raw:
            data = json.loads(transcript_raw)
            transcript = [TranscriptTurn.model_validate(t) for t in data]
        workflow = WorkflowState.model_validate(json.loads(workflow_raw)) if workflow_raw else None
        clarification = json.loads(clarification_raw) if clarification_raw else None
        actor_id = workflow.actor_id if workflow else "unknown"
        return SessionBundle(
            session_id=session_id,
            actor_id=actor_id,
            transcript=transcript,
            workflow=workflow,
            clarification=clarification,
        )

    def save_transcript(self, session_id: str, transcript: list[TranscriptTurn]) -> None:
        key = self._key(session_id, "transcript")
        self.client.setex(key, self.ttl_seconds, json.dumps([t.model_dump() for t in transcript]))
        self._refresh_ttl(session_id)

    def save_workflow(self, session_id: str, workflow: WorkflowState) -> None:
        key = self._key(session_id, "workflow")
        self.client.setex(key, self.ttl_seconds, workflow.model_dump_json())
        self._refresh_ttl(session_id)

    def save_clarification(self, session_id: str, clarification: dict[str, Any] | None) -> None:
        key = self._key(session_id, "clarification")
        if clarification is None:
            self.client.delete(key)
        else:
            self.client.setex(key, self.ttl_seconds, json.dumps(clarification))
        self._refresh_ttl(session_id)

    def append_turn(self, session_id: str, turn: TranscriptTurn) -> None:
        bundle = self.load_session(session_id)
        bundle.transcript.append(turn)
        self.save_transcript(session_id, bundle.transcript)

    def _refresh_ttl(self, session_id: str) -> None:
        for suffix in ("transcript", "workflow", "clarification"):
            key = self._key(session_id, suffix)
            if self.client.exists(key):
                self.client.expire(key, self.ttl_seconds)
