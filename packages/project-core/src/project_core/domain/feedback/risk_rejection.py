"""Normalize Agent III risk rejections for Agent II inbox retries."""

from __future__ import annotations

from typing import Any


def build_risk_rejection_record(
    *,
    query_index: int,
    target_db: str,
    sql: str,
    concerns: list[str] | None,
    risk_feedback: dict[str, Any] | None,
    purpose: str | None = None,
    sql_preview_limit: int = 800,
) -> dict[str, Any]:
    """Build a single rejection record (policy_feedback-shaped) for II retry."""
    fb = risk_feedback if isinstance(risk_feedback, dict) else {}
    concerns_list = [str(c) for c in (concerns or []) if str(c).strip()]
    issue = str(fb.get("issue") or (concerns_list[0] if concerns_list else "semantic_risk"))
    suggestion = fb.get("suggestion")
    record: dict[str, Any] = {
        "query_index": int(query_index),
        "target_db": str(target_db),
        "concerns": concerns_list,
        "issue": issue,
        "rejected_sql": (sql or "")[:sql_preview_limit],
    }
    if purpose:
        record["purpose"] = str(purpose)
    if suggestion is not None and str(suggestion).strip():
        record["suggestion"] = str(suggestion)
    # Preserve extra keys from III (excluding ones we already normalized).
    for key, val in fb.items():
        if key in {"issue", "suggestion"} or key in record:
            continue
        record[key] = val
    return record


def append_risk_rejection(inbox: dict[str, Any], record: dict[str, Any]) -> None:
    """Append to inbox.risk_rejections and set inbox.risk_feedback to latest."""
    existing = inbox.get("risk_rejections")
    if not isinstance(existing, list):
        existing = []
    existing.append(record)
    inbox["risk_rejections"] = existing
    inbox["risk_feedback"] = record
