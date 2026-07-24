"""HTTP A2A server for base-agent template."""

from __future__ import annotations

import os

from agent_core.io.schemas import AgentRequest, AgentResponse
from fastapi import FastAPI
from platform_core.config.loader import load_platform_config

from base_agent.service import build_service

app = FastAPI(title="base-agent")
_service_instance = None


def get_service():
    global _service_instance
    if _service_instance is None:
        config = load_platform_config()
        spec = config.agents["base-agent"]
        _service_instance = build_service(config, spec)
    return _service_instance


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.get("/card")
def card() -> dict:
    # TODO: expose real capabilities from AgentSpec
    return {"name": "base-agent", "capabilities": ["template"], "status": "todo"}


@app.post("/run")
def run(request: AgentRequest) -> AgentResponse:
    return get_service().run(request)


def main() -> None:
    import uvicorn

    host = os.getenv("AGENT_HTTP_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_HTTP_PORT", "8200"))
    uvicorn.run("base_agent.app:app", host=host, port=port)


if __name__ == "__main__":
    main()
