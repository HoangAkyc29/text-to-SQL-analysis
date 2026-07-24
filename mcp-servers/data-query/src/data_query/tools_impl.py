"""data-query MCP — flexible query_rows / aggregate_rows / preview / lookup_distinct."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx

from project_core.domain.analysis import disk_ws
from project_core.domain.analysis.ops.working_set import DatasetWorkingSet
from project_core.domain.contracts.sql_acl import SqlAclContext
from project_core.domain.data_fetch.toolkit import DataFetchToolkit
from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.sql.policy_engine import PolicyEngine

_catalog = SchemaCatalog.from_dictionary_dir()


class _HttpGw:
    def execute_readonly(self, sql: str, acl: SqlAclContext, *, target_db: str = "db2") -> dict[str, Any]:
        base = (os.getenv("SQL_GATEWAY_URL") or "http://localhost:18101").rstrip("/")
        payload = {"sql": sql, "target_db": target_db, **acl.to_gateway_args()}
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(f"{base}/tools/execute_readonly", json=payload)
            resp.raise_for_status()
            return resp.json()


def _acl() -> SqlAclContext:
    raw = os.getenv("DATA_AGENT_ACL_JSON") or "{}"
    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        body = {}
    tables = list(body.get("allowed_tables") or list(_catalog.tables()))
    return SqlAclContext(
        actor_id=str(body.get("actor_id") or os.getenv("DATA_AGENT_ACTOR_ID") or "system"),
        allowed_tables=tables,
        denied_columns=list(body.get("denied_columns") or []),
        store_ids=body.get("store_ids"),
        store_filter_required=bool(body.get("store_filter_required") or False),
        tool_grants=list(body.get("tool_grants") or ["tool:*"]),
    )


def _toolkit() -> DataFetchToolkit:
    acl = _acl()
    ws_root = disk_ws.work_dir()
    ws = DatasetWorkingSet(work_dir=ws_root / "_handles")
    # Hydrate known parquet refs into working set for dataset-ref expansion.
    for prof in disk_ws.list_dataset_profiles(root=ws_root):
        ref = str(prof.get("ref") or "")
        if not ref or ws.has(ref):
            continue
        try:
            df = disk_ws.read_frame(ref, root=ws_root)
            ws.save_frame(ref, df, role="hydrate", source="disk_ws")
        except Exception:  # noqa: BLE001
            continue
    policy = PolicyEngine(
        _catalog,
        allowed_tables=acl.allowed_tables,
        denied_columns=acl.denied_columns or None,
        store_ids=acl.store_ids,
        store_filter_required=acl.store_filter_required,
    )
    return DataFetchToolkit(sql_gateway=_HttpGw(), policy=policy, acl=acl, working_set=ws)


def _run(tool_id: str, args: dict[str, Any], save_as: str | None = None) -> dict[str, Any]:
    brief_raw = os.getenv("DATA_AGENT_BRIEF_JSON") or "{}"
    try:
        brief = json.loads(brief_raw)
    except json.JSONDecodeError:
        brief = {}
    tk = _toolkit()
    out = tk.execute(tool_id, args, save_as=save_as, brief=brief if isinstance(brief, dict) else {})
    if out.get("ok") and out.get("save_as"):
        try:
            df = tk.working_set.get(str(out["save_as"])).frame()
            path = disk_ws.write_frame(str(out["save_as"]), df)
            out["path"] = str(path)
        except Exception as exc:  # noqa: BLE001
            out["disk_warn"] = str(exc)
    return out


def preview_table(
    table: str,
    time_range: dict[str, Any] | None = None,
    columns: list[str] | None = None,
    filters: list[dict[str, Any]] | None = None,
    equals: dict[str, Any] | None = None,
    contains: dict[str, Any] | None = None,
    limit: int = 20,
    save_as: str = "preview",
) -> dict[str, Any]:
    """TOP-N inspect of an allowlisted table (facts require time_range)."""
    return _run(
        "preview_table",
        {
            "table": table,
            "time_range": time_range,
            "columns": columns,
            "filters": filters or [],
            "equals": equals,
            "contains": contains,
            "limit": limit,
        },
        save_as=save_as,
    )


def query_rows(
    table: str,
    time_range: dict[str, Any] | None = None,
    columns: list[str] | None = None,
    filters: list[dict[str, Any]] | None = None,
    order_by: list[Any] | None = None,
    limit: int = 5000,
    sku_ids: Any = None,
    trans_nums: Any = None,
    min_amount: Any = None,
    store_ids: Any = None,
    target_db: str = "auto",
    save_as: str = "query_rows",
) -> dict[str, Any]:
    """Flexible SELECT with filters[] over dictionary-allowlisted tables."""
    return _run(
        "query_rows",
        {
            "table": table,
            "time_range": time_range,
            "columns": columns,
            "filters": filters or [],
            "order_by": order_by,
            "limit": limit,
            "sku_ids": sku_ids,
            "trans_nums": trans_nums,
            "min_amount": min_amount,
            "store_ids": store_ids,
            "target_db": target_db,
        },
        save_as=save_as,
    )


def aggregate_rows(
    table: str = "STRANS",
    time_range: dict[str, Any] | None = None,
    filters: list[dict[str, Any]] | None = None,
    group_by: list[str] | None = None,
    aggs: list[dict[str, Any]] | None = None,
    limit: int = 5000,
    target_db: str = "auto",
    save_as: str = "aggregate_rows",
) -> dict[str, Any]:
    """Server-side GROUP BY aggregates with the same filter rules as query_rows."""
    return _run(
        "aggregate_rows",
        {
            "table": table,
            "time_range": time_range,
            "filters": filters or [],
            "group_by": group_by,
            "aggs": aggs,
            "limit": limit,
            "target_db": target_db,
        },
        save_as=save_as,
    )


def lookup_distinct(
    table: str,
    column: str,
    time_range: dict[str, Any] | None = None,
    contains: str | None = None,
    filters: list[dict[str, Any]] | None = None,
    limit: int = 30,
    save_as: str = "lookup_distinct",
) -> dict[str, Any]:
    """Sample distinct values of a column (optional time pushdown)."""
    return _run(
        "lookup_distinct",
        {
            "table": table,
            "column": column,
            "time_range": time_range,
            "contains": contains,
            "filters": filters or [],
            "limit": limit,
        },
        save_as=save_as,
    )
