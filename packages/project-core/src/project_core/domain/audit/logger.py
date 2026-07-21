from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from project_core.domain.time import utc_now
from project_core.paths import AUDIT_LOG

# Events persisted to audit.jsonl (SQL trail + agent timing spans).
_PERSISTED_EVENT_TYPES = frozenset(
    {
        "sql_execute",
        "sql_explain",
        "sql_policy_reject",
        "agent_ii_plan",
        "schema_retrieve",
        "agent_iii_review",
        "agent_iv_analyze",
        "workflow_timing",
        "case_study_retrieve",
        "case_study_rejected",
    }
)


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
        if event_type.startswith("sql_") or event_type in _PERSISTED_EVENT_TYPES:
            self._append_sql_file(event)

    def log_agent_ii_plan(
        self,
        *,
        trace_id: str,
        actor_id: str,
        payload: dict[str, Any],
        duration_ms: int | None = None,
    ) -> str:
        """Log full Agent II plan (all sql_queries, reasoning, meta) for debugging."""
        event_id = str(uuid4())
        body = {"event_id": event_id, "actor_id": actor_id, **payload}
        if duration_ms is not None:
            body["duration_ms"] = int(duration_ms)
        self.log(
            "agent_ii_plan",
            trace_id=trace_id,
            payload=body,
        )
        return event_id

    def log_schema_retrieve(
        self,
        *,
        trace_id: str,
        actor_id: str,
        payload: dict[str, Any],
        duration_ms: int | None = None,
    ) -> str:
        """Log schema RAG facets + ranked column/table hits (persisted to audit.jsonl)."""
        event_id = str(uuid4())
        body = {"event_id": event_id, "actor_id": actor_id, **payload}
        if duration_ms is not None:
            body["duration_ms"] = int(duration_ms)
        self.log(
            "schema_retrieve",
            trace_id=trace_id,
            payload=body,
        )
        return event_id

    def log_agent_iii_review(
        self,
        *,
        trace_id: str,
        actor_id: str,
        sql_attempt: int,
        query_index: int,
        risk_attempt: int,
        verdict: str,
        duration_ms: int,
        usage_tokens: int = 0,
        concerns: list[str] | None = None,
    ) -> str:
        event_id = str(uuid4())
        self.log(
            "agent_iii_review",
            trace_id=trace_id,
            payload={
                "event_id": event_id,
                "actor_id": actor_id,
                "sql_attempt": sql_attempt,
                "query_index": query_index,
                "risk_attempt": risk_attempt,
                "verdict": verdict,
                "duration_ms": int(duration_ms),
                "usage_tokens": int(usage_tokens or 0),
                "concerns": list(concerns or [])[:8],
            },
        )
        return event_id

    def log_agent_iv_analyze(
        self,
        *,
        trace_id: str,
        actor_id: str,
        sql_attempt: int,
        action: str,
        duration_ms: int,
        usage_tokens: int = 0,
        verification: dict[str, Any] | None = None,
        coverage: dict[str, Any] | None = None,
        artifact_manifests: list[dict[str, Any]] | None = None,
        headline_metrics: dict[str, Any] | None = None,
        recipe_reuse: dict[str, Any] | None = None,
    ) -> str:
        event_id = str(uuid4())
        self.log(
            "agent_iv_analyze",
            trace_id=trace_id,
            payload={
                "event_id": event_id,
                "actor_id": actor_id,
                "sql_attempt": sql_attempt,
                "action": action,
                "duration_ms": int(duration_ms),
                "usage_tokens": int(usage_tokens or 0),
                "verification": dict(verification or {}),
                "coverage": dict(coverage or {}),
                "artifacts": [
                    {
                        "artifact_id": item.get("artifact_id"),
                        "filename": item.get("filename"),
                        "kind": item.get("kind"),
                        "primary": item.get("primary"),
                        "validation_status": item.get("validation_status"),
                    }
                    for item in (artifact_manifests or [])[:20]
                ],
                "headline_metrics": dict(headline_metrics or {}),
                "recipe_reuse": dict(recipe_reuse or {}),
            },
        )
        return event_id

    def log_workflow_timing(
        self,
        *,
        trace_id: str,
        actor_id: str,
        outcome: str,
        pipeline_duration_ms: int,
        step_summary: dict[str, Any],
    ) -> None:
        self.log(
            "workflow_timing",
            trace_id=trace_id,
            payload={
                "actor_id": actor_id,
                "outcome": outcome,
                "pipeline_duration_ms": int(pipeline_duration_ms),
                **step_summary,
            },
        )

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
        duration_ms: int | None = None,
        query_index: int | None = None,
        sql_attempt: int | None = None,
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
        if duration_ms is not None:
            payload["duration_ms"] = int(duration_ms)
        if query_index is not None:
            payload["query_index"] = int(query_index)
        if sql_attempt is not None:
            payload["sql_attempt"] = int(sql_attempt)
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
        duration_ms: int | None = None,
    ) -> None:
        payload: dict[str, Any] = {
            "actor_id": actor_id,
            "sql_hash": hashlib.sha256(sql.encode()).hexdigest()[:16],
            "target_db": target_db,
            "outcome": outcome,
            "violations": violations or [],
        }
        if duration_ms is not None:
            payload["duration_ms"] = int(duration_ms)
        self.log(
            "sql_explain",
            trace_id=trace_id,
            payload=payload,
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
