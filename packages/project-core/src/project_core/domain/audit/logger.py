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
        "data_agent_turn",
        "data_agent_summary",
        "tool_selector_suggest",
        "workflow_timing",
        "case_study_retrieve",
        "case_study_rejected",
    }
)


def safe_args_preview(args: dict[str, Any] | None, *, max_items: int = 8, max_str: int = 120) -> dict[str, Any]:
    """Compact args for audit — no SQL strings, truncate large lists/values."""
    out: dict[str, Any] = {}
    if not isinstance(args, dict):
        return out
    for i, (key, value) in enumerate(args.items()):
        if i >= 24:
            out["_truncated_keys"] = True
            break
        ku = str(key).lower()
        if ku in {"raw_sql", "sql", "query"} or "sql" in ku:
            out[key] = "<redacted>"
            continue
        if isinstance(value, str):
            out[key] = value[:max_str] + ("…" if len(value) > max_str else "")
        elif isinstance(value, list):
            preview = value[:max_items]
            out[key] = {
                "len": len(value),
                "sample": [
                    (v[:max_str] + ("…" if isinstance(v, str) and len(v) > max_str else ""))
                    if isinstance(v, str)
                    else v
                    for v in preview
                ],
            }
        elif isinstance(value, dict):
            nested = {nk: nv for j, (nk, nv) in enumerate(value.items()) if j < max_items}
            out[key] = nested
        else:
            out[key] = value
    return out


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

    def log_data_agent_turn(
        self,
        *,
        trace_id: str,
        actor_id: str,
        turn: int,
        phase: str = "",
        decision: str,
        thought: str = "",
        tool_id: str | None = None,
        op_id: str | None = None,
        ok: bool | None = None,
        error: str | None = None,
        arg_keys: list[str] | None = None,
        row_count: int | None = None,
        save_as: str | None = None,
        server: str | None = None,
        chunk_goal: str | None = None,
        analysis_id: str | None = None,
        args_preview: dict[str, Any] | None = None,
        selector_tool_ids: list[str] | None = None,
        target_dbs: list[str] | None = None,
    ) -> str:
        """Persist one Data Agent CoT/tool turn (no SQL strings)."""
        event_id = str(uuid4())
        payload: dict[str, Any] = {
            "event_id": event_id,
            "actor_id": actor_id,
            "turn": int(turn),
            "phase": phase,
            "decision": decision,
            "thought": (thought or "")[:400],
            "tool_id": tool_id,
            "op_id": op_id,
            "ok": ok,
            "error": (error or "")[:400] or None,
            "arg_keys": list(arg_keys or [])[:40],
            "row_count": row_count,
            "save_as": save_as,
        }
        if server:
            payload["server"] = server
        if chunk_goal:
            payload["chunk_goal"] = chunk_goal[:400]
        if analysis_id:
            payload["analysis_id"] = analysis_id
        if args_preview:
            payload["args_preview"] = safe_args_preview(args_preview)
        if selector_tool_ids is not None:
            payload["selector_tool_ids"] = list(selector_tool_ids)[:20]
        if target_dbs:
            payload["target_dbs"] = list(target_dbs)[:8]
        self.log(
            "data_agent_turn",
            trace_id=trace_id,
            payload=payload,
        )
        return event_id

    def log_tool_selector_suggest(
        self,
        *,
        trace_id: str,
        actor_id: str,
        chunk_goal: str,
        tools: list[dict[str, Any]] | None = None,
        none_available: bool = False,
        reason: str | None = None,
        analysis_id: str | None = None,
        duration_ms: int | None = None,
        use_stub: bool = False,
        usage_tokens: int = 0,
        turn: int | None = None,
    ) -> str:
        """Persist one Tool-Selector suggestion (no execute)."""
        event_id = str(uuid4())
        cleaned: list[dict[str, Any]] = []
        for tip in tools or []:
            if not isinstance(tip, dict):
                continue
            cleaned.append(
                {
                    "server": tip.get("server"),
                    "tool_id": tip.get("tool_id"),
                    "reason": str(tip.get("reason") or "")[:200],
                    "args_hints": safe_args_preview(
                        tip.get("args_hints") if isinstance(tip.get("args_hints"), dict) else tip.get("args")
                    ),
                }
            )
            if len(cleaned) >= 12:
                break
        body: dict[str, Any] = {
            "event_id": event_id,
            "actor_id": actor_id,
            "chunk_goal": (chunk_goal or "")[:400],
            "tools": cleaned,
            "none_available": bool(none_available),
            "reason": (reason or "")[:300] or None,
            "use_stub": bool(use_stub),
            "usage_tokens": int(usage_tokens or 0),
        }
        if analysis_id:
            body["analysis_id"] = analysis_id
        if duration_ms is not None:
            body["duration_ms"] = int(duration_ms)
        if turn is not None:
            body["turn"] = int(turn)
        self.log("tool_selector_suggest", trace_id=trace_id, payload=body)
        return event_id

    def log_data_agent_summary(
        self,
        *,
        trace_id: str,
        actor_id: str,
        action: str,
        duration_ms: int,
        usage_tokens: int = 0,
        planner_turns: int = 0,
        fetch_ok: int = 0,
        fetch_attempts: int = 0,
        fetch_errors: list[str] | None = None,
        steps_trace: list[dict[str, Any]] | None = None,
        caveats: list[str] | None = None,
        artifact_count: int = 0,
        use_stub: bool = False,
        analysis_id: str | None = None,
        stages: list[dict[str, Any]] | None = None,
        tool_chain: list[dict[str, Any]] | None = None,
        coverage: dict[str, Any] | None = None,
    ) -> str:
        """Persist end-of-loop Data Agent summary for monitoring."""
        event_id = str(uuid4())
        body: dict[str, Any] = {
            "event_id": event_id,
            "actor_id": actor_id,
            "action": action,
            "duration_ms": int(duration_ms),
            "usage_tokens": int(usage_tokens or 0),
            "planner_turns": int(planner_turns),
            "fetch_ok": int(fetch_ok),
            "fetch_attempts": int(fetch_attempts),
            "fetch_errors": [str(e)[:200] for e in (fetch_errors or [])][:20],
            "steps_trace": list(steps_trace or [])[:40],
            "caveats": list(caveats or [])[:20],
            "artifact_count": int(artifact_count),
            "use_stub": bool(use_stub),
        }
        if analysis_id:
            body["analysis_id"] = analysis_id
        if stages:
            body["stages"] = list(stages)[:40]
        if tool_chain:
            # Compact chain for audit (no giant samples).
            compact_chain: list[dict[str, Any]] = []
            for step in tool_chain[:40]:
                if not isinstance(step, dict):
                    continue
                compact_chain.append(
                    {
                        "kind": step.get("kind"),
                        "server": step.get("server"),
                        "tool_id": step.get("tool_id") or step.get("op_id"),
                        "save_as": step.get("save_as"),
                        "args": safe_args_preview(step.get("args") if isinstance(step.get("args"), dict) else None),
                    }
                )
            body["tool_chain"] = compact_chain
        if coverage:
            body["coverage"] = {
                "ok": coverage.get("ok"),
                "gaps": list(coverage.get("gaps") or [])[:12],
                "caveats": list(coverage.get("caveats") or [])[:12],
                "row_count": coverage.get("row_count"),
                "top_n": coverage.get("top_n"),
                "source": coverage.get("source"),
            }
        self.log(
            "data_agent_summary",
            trace_id=trace_id,
            payload=body,
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
