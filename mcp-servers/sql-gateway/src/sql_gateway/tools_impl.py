from __future__ import annotations

import os
import threading
import time
from collections import defaultdict
from typing import Any

import pyodbc

from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.sql.policy_engine import PolicyEngine

_catalog = SchemaCatalog.from_dictionary_dir()
_rate_lock = threading.Lock()
_rate_buckets: dict[str, list[float]] = defaultdict(list)
_semaphore = threading.Semaphore(int(os.getenv("SQL_GATEWAY_MAX_CONCURRENT", "8")))


def _rate_limit(actor_id: str, *, limit: int = 30, window: int = 60) -> None:
    now = time.time()
    with _rate_lock:
        bucket = [t for t in _rate_buckets[actor_id] if now - t < window]
        if len(bucket) >= limit:
            raise RuntimeError("rate_limit_exceeded")
        bucket.append(now)
        _rate_buckets[actor_id] = bucket


def _policy(actor_id: str) -> PolicyEngine:
    return PolicyEngine(_catalog, allowed_tables=_catalog.tables())


def _connect() -> pyodbc.Connection:
    dsn = os.getenv("ANALYTICS_DB_DSN")
    if not dsn:
        raise RuntimeError("ANALYTICS_DB_DSN not configured")
    return pyodbc.connect(dsn, timeout=30)


def validate_sql(sql: str, actor_id: str = "system") -> dict[str, Any]:
    """Run PolicyEngine validation for a SQL statement."""
    verdict = _policy(actor_id).validate(sql)
    return {
        "allowed": verdict.allowed,
        "violations": verdict.violations,
        "sanitized_sql": verdict.sanitized_sql,
    }


def explain_sql(sql: str, actor_id: str = "system") -> dict[str, Any]:
    """Return SHOWPLAN-style explanation (best effort)."""
    _rate_limit(actor_id)
    try:
        with _semaphore, _connect() as conn:
            cur = conn.cursor()
            cur.execute(f"SET SHOWPLAN_ALL ON; {sql}")
            rows = cur.fetchall() if cur.description else []
            return {"plan_rows": len(rows), "status": "ok"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)[:500]}


def execute_readonly(sql: str, actor_id: str = "system") -> dict[str, Any]:
    """Execute validated readonly SQL and return rows as dicts."""
    _rate_limit(actor_id)
    verdict = _policy(actor_id).validate(sql)
    if not verdict.allowed:
        return {"error": "policy_blocked", "violations": verdict.violations}
    sanitized = verdict.sanitized_sql or sql
    with _semaphore, _connect() as conn:
        cur = conn.cursor()
        cur.execute(sanitized)
        columns = [c[0] for c in cur.description] if cur.description else []
        rows = [dict(zip(columns, row, strict=False)) for row in cur.fetchmany(50000)]
        return {"columns": columns, "rows": rows, "row_count": len(rows)}


def get_schema_snapshot(actor_id: str = "system") -> dict[str, Any]:
    """Return compact schema metadata for risk review."""
    return {"tables": _catalog.snapshot()}
