from __future__ import annotations

import os
import threading
import time
from collections import defaultdict
from typing import Any

import pyodbc

from project_core.domain.access.permission_set import grant_denial
from project_core.domain.contracts.sql_acl import SqlAclContext
from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.sql.policy_engine import PolicyEngine
from project_core.text.tcvn3 import maybe_decode_row

_catalog = SchemaCatalog.from_dictionary_dir()
_rate_lock = threading.Lock()
_rate_buckets: dict[str, list[float]] = defaultdict(list)
_semaphore = threading.Semaphore(int(os.getenv("SQL_GATEWAY_MAX_CONCURRENT", "8")))

_DSN_BY_DB = {
    "db1": "ANALYTICS_DB_DSN",
    "db2": "ANALYTICS_DB_DSN_2",
}


def _rate_limit(actor_id: str, *, limit: int = 30, window: int = 60) -> None:
    now = time.time()
    with _rate_lock:
        bucket = [t for t in _rate_buckets[actor_id] if now - t < window]
        if len(bucket) >= limit:
            raise RuntimeError("rate_limit_exceeded")
        bucket.append(now)
        _rate_buckets[actor_id] = bucket


def _acl_from_kwargs(
    actor_id: str = "system",
    *,
    allowed_tables: list[str] | None = None,
    denied_columns: list[str] | None = None,
    store_ids: list[int] | None = None,
    store_filter_required: bool = False,
    tool_grants: list[str] | None = None,
    acl: SqlAclContext | None = None,
) -> SqlAclContext:
    if acl is not None:
        return acl
    return SqlAclContext(
        actor_id=actor_id,
        allowed_tables=list(allowed_tables or []),
        denied_columns=list(denied_columns or []),
        store_ids=store_ids,
        store_filter_required=store_filter_required,
        tool_grants=list(tool_grants or []),
    )


def _tool_denied(ctx: SqlAclContext, action: str) -> dict[str, Any] | None:
    """Default-deny tool-grant gate.

    Every real caller (chat-gateway ``HttpSqlGatewayClient`` over HTTP or
    in-process) forwards ``tool_grants`` via ``SqlAclContext.to_gateway_args``,
    so an empty grant set means the caller is unauthorized and is denied.
    """
    return grant_denial(
        ctx.tool_grants,
        f"tool:sql-gateway:{action}",
        f"tool_not_granted:sql-gateway:{action}",
    )


def _policy(acl: SqlAclContext) -> PolicyEngine:
    return PolicyEngine(
        _catalog,
        allowed_tables=acl.allowed_tables,
        denied_columns=acl.denied_columns or None,
        store_ids=acl.store_ids,
        store_filter_required=acl.store_filter_required,
    )


def _resolve_target_db(target_db: str | None) -> str:
    if not target_db:
        return "db1"
    normalized = target_db.lower().strip()
    if normalized in ("db2", "2"):
        return "db2"
    return "db1"


def _connect(target_db: str = "db1") -> pyodbc.Connection:
    db = _resolve_target_db(target_db)
    key = _DSN_BY_DB[db]
    dsn = os.getenv(key)
    if not dsn:
        raise RuntimeError(f"{key} not configured (target_db={db})")
    return pyodbc.connect(dsn, timeout=30)


def validate_sql(
    sql: str,
    actor_id: str = "system",
    *,
    allowed_tables: list[str] | None = None,
    denied_columns: list[str] | None = None,
    store_ids: list[int] | None = None,
    store_filter_required: bool = False,
    tool_grants: list[str] | None = None,
    acl: SqlAclContext | None = None,
) -> dict[str, Any]:
    """Run PolicyEngine validation for a SQL statement (dry check)."""
    ctx = _acl_from_kwargs(
        actor_id,
        allowed_tables=allowed_tables,
        denied_columns=denied_columns,
        store_ids=store_ids,
        store_filter_required=store_filter_required,
        tool_grants=tool_grants,
        acl=acl,
    )
    denied = _tool_denied(ctx, "validate")
    if denied is not None:
        return denied
    verdict = _policy(ctx).validate(sql)
    return {
        "allowed": verdict.allowed,
        "violations": verdict.violations,
        "sanitized_sql": verdict.sanitized_sql,
    }


def explain_sql(
    sql: str,
    actor_id: str = "system",
    target_db: str = "db1",
    *,
    allowed_tables: list[str] | None = None,
    denied_columns: list[str] | None = None,
    store_ids: list[int] | None = None,
    store_filter_required: bool = False,
    tool_grants: list[str] | None = None,
    acl: SqlAclContext | None = None,
) -> dict[str, Any]:
    """Return SHOWPLAN-style explanation after policy validation."""
    ctx = _acl_from_kwargs(
        actor_id,
        allowed_tables=allowed_tables,
        denied_columns=denied_columns,
        store_ids=store_ids,
        store_filter_required=store_filter_required,
        tool_grants=tool_grants,
        acl=acl,
    )
    denied = _tool_denied(ctx, "explain")
    if denied is not None:
        return denied
    _rate_limit(ctx.actor_id)
    verdict = _policy(ctx).validate(sql)
    if not verdict.allowed:
        return {"status": "policy_blocked", "violations": verdict.violations}
    sanitized = verdict.sanitized_sql or sql
    db = _resolve_target_db(target_db)
    try:
        with _semaphore, _connect(db) as conn:
            cur = conn.cursor()
            cur.execute(f"SET SHOWPLAN_ALL ON; {sanitized}")
            rows = cur.fetchall() if cur.description else []
            return {"plan_rows": len(rows), "status": "ok", "target_db": db}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)[:500]}


def execute_readonly(
    sql: str,
    actor_id: str = "system",
    target_db: str = "db1",
    *,
    allowed_tables: list[str] | None = None,
    denied_columns: list[str] | None = None,
    store_ids: list[int] | None = None,
    store_filter_required: bool = False,
    tool_grants: list[str] | None = None,
    acl: SqlAclContext | None = None,
) -> dict[str, Any]:
    """Execute validated readonly SQL and return rows as dicts."""
    ctx = _acl_from_kwargs(
        actor_id,
        allowed_tables=allowed_tables,
        denied_columns=denied_columns,
        store_ids=store_ids,
        store_filter_required=store_filter_required,
        tool_grants=tool_grants,
        acl=acl,
    )
    denied = _tool_denied(ctx, "execute")
    if denied is not None:
        return denied
    _rate_limit(ctx.actor_id)
    db = _resolve_target_db(target_db)
    verdict = _policy(ctx).validate(sql)
    if not verdict.allowed:
        return {"error": "policy_blocked", "violations": verdict.violations}
    sanitized = verdict.sanitized_sql or sql
    with _semaphore, _connect(db) as conn:
        cur = conn.cursor()
        cur.execute(sanitized)
        columns = [c[0] for c in cur.description] if cur.description else []
        # Decode legacy TCVN3 text at the SQL boundary so every downstream
        # consumer (agents, parquet, Excel export) sees correct Unicode.
        rows = [
            maybe_decode_row(dict(zip(columns, row, strict=False)))
            for row in cur.fetchmany(50000)
        ]
        return {"columns": columns, "rows": rows, "row_count": len(rows), "target_db": db}


def get_schema_snapshot(
    actor_id: str = "system",
    allowed_tables: list[str] | None = None,
    *,
    denied_columns: list[str] | None = None,
    store_ids: list[int] | None = None,
    store_filter_required: bool = False,
    tool_grants: list[str] | None = None,
    acl: SqlAclContext | None = None,
) -> dict[str, Any]:
    """Return schema metadata from data_dictionary for agents."""
    ctx = _acl_from_kwargs(
        actor_id,
        allowed_tables=allowed_tables,
        denied_columns=denied_columns,
        store_ids=store_ids,
        store_filter_required=store_filter_required,
        tool_grants=tool_grants,
        acl=acl,
    )
    denied = _tool_denied(ctx, "explain")
    if denied is not None:
        return denied
    role = list(ctx.allowed_tables)
    bundle = _catalog.agent_schema_bundle(role) if role else {"tables": [], "domain_definitions_excerpt": ""}
    return {
        **bundle,
        "logical_tables": _catalog.logical_table_names(),
    }
