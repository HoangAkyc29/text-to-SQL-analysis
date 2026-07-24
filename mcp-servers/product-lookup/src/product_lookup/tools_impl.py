"""product-lookup MCP tools — resolve_products via sql-gateway HTTP."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx
import pandas as pd

from project_core.domain.analysis import disk_ws
from project_core.domain.contracts.sql_acl import SqlAclContext
from project_core.domain.data_fetch import builders
from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.sql.policy_engine import PolicyEngine

_catalog = SchemaCatalog.from_dictionary_dir()


def _acl_from_env() -> SqlAclContext:
    raw = os.getenv("DATA_AGENT_ACL_JSON") or "{}"
    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        body = {}
    return SqlAclContext(
        actor_id=str(body.get("actor_id") or os.getenv("DATA_AGENT_ACTOR_ID") or "system"),
        allowed_tables=list(body.get("allowed_tables") or []),
        denied_columns=list(body.get("denied_columns") or []),
        store_ids=body.get("store_ids"),
        store_filter_required=bool(body.get("store_filter_required") or False),
        tool_grants=list(body.get("tool_grants") or ["tool:*"]),
    )


def _execute_sql(sql: str, *, target_db: str = "db2") -> dict[str, Any]:
    base = (os.getenv("SQL_GATEWAY_URL") or "http://localhost:18101").rstrip("/")
    acl = _acl_from_env()
    payload = {"sql": sql, "target_db": target_db, **acl.to_gateway_args()}
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(f"{base}/tools/execute_readonly", json=payload)
        resp.raise_for_status()
        return resp.json()


def resolve_products(
    codes: list[str] | str,
    limit: int = 50,
    save_as: str = "resolved_products",
) -> dict[str, Any]:
    """Lookup SKU_DEF by display product codes → SKU_ID, SKU_CODE, FULL_NAME."""
    code_list = codes if isinstance(codes, list) else [codes]
    acl = _acl_from_env()
    sql = builders.build_resolve_products(codes=code_list, limit=limit)
    policy = PolicyEngine(
        _catalog,
        allowed_tables=acl.allowed_tables or list(_catalog.tables()),
        denied_columns=acl.denied_columns or None,
        store_ids=acl.store_ids,
        store_filter_required=acl.store_filter_required,
    )
    verdict = policy.validate(sql)
    if not verdict.allowed:
        return {"ok": False, "error": "policy_blocked", "violations": list(verdict.violations)}
    result = _execute_sql(verdict.sanitized_sql or sql, target_db="db2")
    if result.get("error"):
        return {"ok": False, "error": str(result.get("error")), "message": result.get("message")}
    rows = list(result.get("rows") or [])
    cols = list(result.get("columns") or [])
    df = pd.DataFrame(rows, columns=cols) if cols else pd.DataFrame(rows)
    path = disk_ws.write_frame(save_as, df)
    return {
        "ok": True,
        "tool_id": "resolve_products",
        "save_as": save_as,
        "row_count": int(len(df)),
        "columns": list(df.columns),
        "sample": disk_ws.sample_records(df),
        "path": str(path),
        "target_db": "db2",
    }
