from __future__ import annotations

import os

from agent_core.io.schemas import AgentRequest, AgentResponse
from fastapi import FastAPI
from platform_core.config.loader import load_platform_config

from risk_reviewer.service import build_service

app = FastAPI(title="risk-reviewer")
_service = None


def get_service():
    global _service
    if _service is None:
        config = load_platform_config(os.getenv("PLATFORM_CONFIG", "platform-supermarket.yaml"))
        _service = build_service(config, config.agents["risk-reviewer"])
    return _service


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/run")
def run(request: AgentRequest) -> AgentResponse:
    return get_service().run(request)


def main() -> None:
    import uvicorn

    uvicorn.run("risk_reviewer.app:app", host="0.0.0.0", port=int(os.getenv("AGENT_HTTP_PORT", "8203")))
