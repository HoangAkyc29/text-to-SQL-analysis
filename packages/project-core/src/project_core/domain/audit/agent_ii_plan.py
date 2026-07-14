from __future__ import annotations

import hashlib
from typing import Any

from project_core.domain.contracts.agent_outputs import SqlPlannerResponse


def build_agent_ii_plan_payload(
    parsed: SqlPlannerResponse,
    *,
    sql_attempt: int,
    usage_tokens: int = 0,
) -> dict[str, Any]:
    """Serialize Agent II plan for audit / workflow (full SQL, not preview-only)."""
    queries: list[dict[str, Any]] = []
    default_db = parsed.target_db or "db2"
    for idx, sql in enumerate(parsed.sql_queries):
        meta = parsed.query_meta[idx] if idx < len(parsed.query_meta) else {}
        target_db = parsed.target_dbs[idx] if idx < len(parsed.target_dbs) else default_db
        queries.append(
            {
                "query_index": idx,
                "sql": sql,
                "sql_hash": hashlib.sha256(sql.encode()).hexdigest()[:16],
                "target_db": target_db,
                "query_meta": meta,
            }
        )
    return {
        "sql_attempt": sql_attempt,
        "action": parsed.action,
        "target_db": parsed.target_db,
        "reasoning": parsed.reasoning,
        "reason": parsed.reason,
        "schema_tables_used": list(parsed.schema_tables_used),
        "semantic_keys_used": list(parsed.semantic_keys_used),
        "selected_tables": list(parsed.selected_tables),
        "selected_target_dbs": list(parsed.selected_target_dbs),
        "queries": queries,
        "usage_tokens": usage_tokens,
        "clarification_request": parsed.clarification_request,
    }


def plan_sql_workflow_summary(payload: dict[str, Any], *, max_reasoning: int = 240) -> str:
    """Compact summary for WorkflowStep — full detail lives in audit event."""
    action = payload.get("action", "?")
    n = len(payload.get("queries") or [])
    attempt = payload.get("sql_attempt", "?")
    parts = [f"action={action}", f"sql_attempt={attempt}", f"n_queries={n}"]
    reasoning = payload.get("reasoning")
    if isinstance(reasoning, str) and reasoning.strip():
        text = reasoning.strip().replace("\n", " ")
        if len(text) > max_reasoning:
            text = text[: max_reasoning - 3] + "..."
        parts.append(f"reasoning={text}")
    elif payload.get("reason"):
        parts.append(f"reason={str(payload['reason'])[:120]}")
    return ";".join(parts)
