"""HTTP surface for sql-gateway tools (used by chat-gateway HttpSqlGatewayClient)."""

from __future__ import annotations

import inspect
from typing import Any

from fastapi import Depends, FastAPI
from project_core.config.env import load_project_env
from project_core.infra.auth_internal import verify_internal_service

from sql_gateway import tools_impl as impl

load_project_env()

app = FastAPI(title="sql-gateway-http")


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/tools/{tool_name}")
def invoke_tool(
    tool_name: str,
    body: dict[str, Any],
    _: None = Depends(verify_internal_service),
) -> dict[str, Any]:
    fn = getattr(impl, tool_name, None)
    if fn is None or not inspect.isfunction(fn) or fn.__module__ != impl.__name__:
        return {"error": "unknown_tool", "tool": tool_name}
    sig = inspect.signature(fn)
    allowed = {k: v for k, v in body.items() if k in sig.parameters}
    return fn(**allowed)


def main() -> None:
    import os
    import uvicorn

    uvicorn.run(
        "sql_gateway.http_app:app",
        host="0.0.0.0",
        port=int(os.getenv("SQL_GATEWAY_HTTP_PORT", "8101")),
    )


if __name__ == "__main__":
    main()
