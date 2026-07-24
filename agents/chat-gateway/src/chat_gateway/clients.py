from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx
from agent_core.io.schemas import AgentRequest
from pydantic_core import to_jsonable_python

from project_core.domain.budget import AgentInvoker, SqlGatewayClient
from project_core.domain.contracts.sql_acl import SqlAclContext
from project_core.domain.errors.codes import AgentUnavailableError
from project_core.infra.auth_internal import internal_auth_headers
from project_core.infra.resilience import CircuitBreaker

logger = logging.getLogger(__name__)


def _jsonable_fallback(value: Any) -> Any:
    """Convert numpy/pandas scalars and other odd types for AgentRequest payloads."""
    item = getattr(value, "item", None)
    if callable(item):
        try:
            return item()
        except Exception:  # noqa: BLE001
            pass
    return str(value)


def dumps_agent_payload(payload: dict[str, Any]) -> str:
    return json.dumps(to_jsonable_python(payload, fallback=_jsonable_fallback))


class HttpAgentInvoker(AgentInvoker):
    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        circuit: CircuitBreaker | None = None,
        trace_id: str | None = None,
        analysis_id: str | None = None,
    ) -> None:
        self.urls = {
            "I": os.getenv("AGENT_I_URL", "http://localhost:18201"),
            "II": os.getenv("AGENT_II_URL", "http://localhost:18202"),
            "III": os.getenv("AGENT_III_URL", "http://localhost:18203"),
            "IV": os.getenv("AGENT_IV_URL", "http://localhost:18204"),
            "DATA": os.getenv("AGENT_DATA_URL", "http://localhost:18206"),
            "TOOL_SELECTOR": os.getenv("AGENT_TOOL_SELECTOR_URL", "http://localhost:18205"),
        }
        self._client = client
        self._owns_client = client is None
        self._circuit = circuit or CircuitBreaker()
        self._trace_id = trace_id
        self._analysis_id = analysis_id

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=600.0)
        return self._client

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()
            self._client = None

    def set_trace(self, *, trace_id: str | None = None, analysis_id: str | None = None) -> None:
        if trace_id is not None:
            self._trace_id = trace_id
        if analysis_id is not None:
            self._analysis_id = analysis_id

    def invoke(self, agent: str, payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        if self._circuit.is_open():
            raise AgentUnavailableError(f"Circuit open for agent {agent}")
        url = f"{self.urls[agent]}/run"
        req = AgentRequest(
            session_id=metadata.get("session_id", "system"),
            actor_id=metadata.get("actor_id", "system"),
            message=dumps_agent_payload(payload),
            metadata={
                **metadata,
                **({"trace_id": self._trace_id} if self._trace_id else {}),
                **({"analysis_id": self._analysis_id} if self._analysis_id else {}),
            },
        )
        headers = {**internal_auth_headers()}
        if self._trace_id:
            headers["X-Trace-Id"] = self._trace_id
        if self._analysis_id:
            headers["X-Analysis-Id"] = self._analysis_id
        try:
            resp = self._get_client().post(url, json=req.model_dump(), headers=headers)
            resp.raise_for_status()
            data = resp.json()
            self._circuit.record_success()
        except Exception:
            self._circuit.record_failure()
            raise
        usage = int((data.get("metadata") or {}).get("usage_tokens") or 0)
        if usage:
            out_meta = data.setdefault("metadata", {})
            out_meta["usage_tokens"] = usage
        out = data.get("payload") or {}
        if not out and data.get("content"):
            try:
                out = __import__("json").loads(data["content"])
            except __import__("json").JSONDecodeError:
                out = {"content": data["content"]}
        return out


class HttpSqlGatewayClient(SqlGatewayClient):
    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        circuit: CircuitBreaker | None = None,
        trace_id: str | None = None,
    ) -> None:
        self.base = os.getenv("SQL_GATEWAY_URL", "http://localhost:18101")
        self._client = client
        self._owns_client = client is None
        self._circuit = circuit or CircuitBreaker()
        self._trace_id = trace_id

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=60.0)
        return self._client

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()
            self._client = None

    def set_trace(self, trace_id: str | None) -> None:
        self._trace_id = trace_id

    def _call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if self._circuit.is_open():
            raise AgentUnavailableError(f"Circuit open for sql-gateway tool {tool}")
        if os.getenv("SQL_GATEWAY_INPROCESS") == "1":
            from sql_gateway import tools_impl as impl

            fn = getattr(impl, tool)
            return fn(**arguments)
        headers = {**internal_auth_headers()}
        if self._trace_id:
            headers["X-Trace-Id"] = self._trace_id
        try:
            resp = self._get_client().post(f"{self.base}/tools/{tool}", json=arguments, headers=headers)
            if resp.status_code == 404:
                logger.warning("sql-gateway HTTP 404 for %s — check SQL_GATEWAY_URL", tool)
                return {"error": "gateway_not_found", "status": 404}
            resp.raise_for_status()
            self._circuit.record_success()
            return resp.json()
        except Exception:
            self._circuit.record_failure()
            raise

    def _acl_args(self, acl: SqlAclContext) -> dict[str, Any]:
        return acl.to_gateway_args()

    def validate_sql(self, sql: str, acl: SqlAclContext) -> dict[str, Any]:
        return self._call("validate_sql", {"sql": sql, **self._acl_args(acl)})

    def explain_sql(self, sql: str, acl: SqlAclContext, *, target_db: str = "db2") -> dict[str, Any]:
        return self._call(
            "explain_sql",
            {"sql": sql, "target_db": target_db, **self._acl_args(acl)},
        )

    def execute_readonly(self, sql: str, acl: SqlAclContext, *, target_db: str = "db2") -> dict[str, Any]:
        return self._call(
            "execute_readonly",
            {"sql": sql, "target_db": target_db, **self._acl_args(acl)},
        )
