"""Template agent service — subclass BaseAgentService and implement decide()."""

from __future__ import annotations

import json
from pathlib import Path

from agent_core.io.schemas import AgentRequest, AgentResponse
from platform_core.config.schema import AgentSpec, PlatformConfig
from platform_core.service.base import BaseAgentService, DecisionContext

# TODO: import domain tools, project_core helpers, model provider as needed
# from project_core.models.provider import attach_model_provider


class BaseAgentTemplateService(BaseAgentService):
    """Scaffold agent — replace decide() with real domain logic."""

    def decide(self, ctx: DecisionContext) -> AgentResponse:
        """
        TODO checklist for a real agent:
        - Parse run metadata from ctx.request
        - Call MCP tools via ctx.mcp / ctx.tools
        - Run Strands turn if using LLM (project_core.runtime.strands_runner)
        - Return AgentResponse with payload for downstream graph nodes
        """
        payload = {
            "status": "todo",
            "message": "Implement BaseAgentTemplateService.decide()",
            "goal": ctx.request.goal,
        }
        return AgentResponse(
            session_id=ctx.request.session_id,
            actor_id=ctx.request.actor_id,
            content=json.dumps(payload),
            payload=payload,
        )


def build_service(config: PlatformConfig, spec: AgentSpec) -> BaseAgentTemplateService:
    """Factory registered in platform.yaml as base_agent.service:build_service."""
    skills_root = Path(__file__).resolve().parent / "skills"
    service = BaseAgentTemplateService(config, spec, skills_root=skills_root)
    # TODO: attach_model_provider(service, config_root=...)
    return service
