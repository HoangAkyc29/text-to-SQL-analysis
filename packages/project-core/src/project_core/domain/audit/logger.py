from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from project_core.domain.time import utc_now
from project_core.paths import AUDIT_LOG


class AuditLogger:
    def __init__(self, sink: list[dict[str, Any]] | None = None) -> None:
        self._events = sink if sink is not None else []
        self._sql_path = os.getenv("SQL_AUDIT_LOG_PATH") or str(AUDIT_LOG)

    def log(self, event_type: str, *, trace_id: str | None = None, payload: dict[str, Any] | None = None) -> None:
        event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "trace_id": trace_id,
            "payload": payload or {},
            "at": utc_now().isoformat(),
        }
        self._events.append(event)
        if event_type.startswith("sql_") or event_type in {"agent_ii_plan", "schema_retrieve"}:
            self._append_sql_file(event)

    def log_agent_ii_plan(
        self,
        *,
        trace_id: str,
        actor_id: str,
        payload: dict[str, Any],
    ) -> str:
        """Log full Agent II plan (all sql_queries, reasoning, meta) for debugging."""
        event_id = str(uuid4())
        self.log(
            "agent_ii_plan",
            trace_id=trace_id,
            payload={"event_id": event_id, "actor_id": actor_id, **payload},
        )
        return event_id

    def log_schema_retrieve(
        self,
        *,
        trace_id: str,
        actor_id: str,
        payload: dict[str, Any],
    ) -> str:
        """Log schema RAG facets + ranked column/table hits (persisted to audit.jsonl)."""
        event_id = str(uuid4())
        self.log(
            "schema_retrieve",
            trace_id=trace_id,
            payload={"event_id": event_id, "actor_id": actor_id, **payload},
        )
        return event_id

    def log_sql_execute(
        self,
        *,
        trace_id: str,
        actor_id: str,
        role: str,
        sql: str,
        target_db: str,
        row_count: int,
        outcome: str,
        violations: list[str] | None = None,
        error_message: str | None = None,
    ) -> None:
        payload: dict[str, Any] = {
            "actor_id": actor_id,
            "role": role,
            "sql": sql,
            "sql_hash": hashlib.sha256(sql.encode()).hexdigest()[:16],
            "target_db": target_db,
            "row_count": row_count,
            "outcome": outcome,
            "violations": violations or [],
        }
        if error_message:
            payload["error_message"] = error_message[:500]
        self.log(
            "sql_execute",
            trace_id=trace_id,
            payload=payload,
        )

    def log_sql_explain(
        self,
        *,
        trace_id: str,
        actor_id: str,
        sql: str,
        target_db: str,
        outcome: str,
        violations: list[str] | None = None,
    ) -> None:
        self.log(
            "sql_explain",
            trace_id=trace_id,
            payload={
                "actor_id": actor_id,
                "sql_hash": hashlib.sha256(sql.encode()).hexdigest()[:16],
                "target_db": target_db,
                "outcome": outcome,
                "violations": violations or [],
            },
        )

    def log_sql_policy_reject(
        self,
        *,
        trace_id: str,
        actor_id: str,
        sql: str,
        target_db: str,
        violations: list[str],
        query_index: int,
    ) -> None:
        self.log(
            "sql_policy_reject",
            trace_id=trace_id,
            payload={
                "actor_id": actor_id,
                "sql": sql,
                "sql_hash": hashlib.sha256(sql.encode()).hexdigest()[:16],
                "sql_preview": sql[:300],
                "target_db": target_db,
                "violations": violations,
                "query_index": query_index,
            },
        )

    def _append_sql_file(self, event: dict[str, Any]) -> None:
        try:
            path = Path(self._sql_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        except OSError:
            pass

    def events(self) -> list[dict[str, Any]]:
        return list(self._events)
