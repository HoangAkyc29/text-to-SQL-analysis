from __future__ import annotations

import json
import os
from typing import Any
from uuid import uuid4

import httpx
from agent_core.io.schemas import AgentRequest

from project_core.domain.budget import AgentInvoker, SqlGatewayClient


class HttpAgentInvoker(AgentInvoker):
    def __init__(self) -> None:
        self.urls = {
            "I": os.getenv("AGENT_I_URL", "http://localhost:8201"),
            "II": os.getenv("AGENT_II_URL", "http://localhost:8202"),
            "III": os.getenv("AGENT_III_URL", "http://localhost:8203"),
            "IV": os.getenv("AGENT_IV_URL", "http://localhost:8204"),
        }

    def invoke(self, agent: str, payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.urls[agent]}/run"
        req = AgentRequest(
            session_id=metadata.get("session_id", "system"),
            actor_id=metadata.get("actor_id", "system"),
            message=json.dumps(payload),
            metadata=metadata,
        )
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(url, json=req.model_dump())
            resp.raise_for_status()
            data = resp.json()
        out = data.get("payload") or {}
        if not out and data.get("content"):
            try:
                out = json.loads(data["content"])
            except json.JSONDecodeError:
                out = {"content": data["content"]}
        return out


class HttpSqlGatewayClient(SqlGatewayClient):
    def __init__(self) -> None:
        self.base = os.getenv("SQL_GATEWAY_URL", "http://localhost:8101")

    def _call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        # Direct import fallback for in-process dev without MCP HTTP surface.
        if os.getenv("SQL_GATEWAY_INPROCESS") == "1":
            from sql_gateway import tools_impl as impl

            fn = getattr(impl, tool)
            return fn(**arguments)
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(f"{self.base}/tools/{tool}", json=arguments)
            if resp.status_code == 404:
                from sql_gateway import tools_impl as impl

                fn = getattr(impl, tool)
                return fn(**arguments)
            resp.raise_for_status()
            return resp.json()

    def validate_sql(self, sql: str, actor_id: str) -> dict[str, Any]:
        return self._call("validate_sql", {"sql": sql, "actor_id": actor_id})

    def explain_sql(self, sql: str, actor_id: str) -> dict[str, Any]:
        return self._call("explain_sql", {"sql": sql, "actor_id": actor_id})

    def execute_readonly(self, sql: str, actor_id: str) -> dict[str, Any]:
        return self._call("execute_readonly", {"sql": sql, "actor_id": actor_id})
