from __future__ import annotations

import os

from agent_core.io.schemas import AgentRequest, AgentResponse
from fastapi import Depends, FastAPI
from platform_core.config.loader import load_platform_config
from project_core.config.env import load_project_env
from project_core.infra.auth_internal import verify_internal_service

from conversational_router.service import build_service

load_project_env()

app = FastAPI(title="conversational-router")
_service = None


def get_service():
    global _service
    if _service is None:
        config = load_platform_config(os.getenv("PLATFORM_CONFIG", "platform-supermarket.yaml"))
        spec = config.agents["conversational-router"]
        _service = build_service(config, spec)
    return _service


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/run")
def run(request: AgentRequest, _: None = Depends(verify_internal_service)) -> AgentResponse:
    return get_service().run(request)


def main() -> None:
    import uvicorn

    uvicorn.run("conversational_router.app:app", host="0.0.0.0", port=int(os.getenv("AGENT_HTTP_PORT", "18201")))


if __name__ == "__main__":
    main()
