from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_core.io.schemas import AgentRequest, AgentResponse
from platform_core.config.schema import AgentSpec, PlatformConfig
from platform_core.service.base import BaseAgentService, DecisionContext

from project_core.domain.access.context_policy import ContextPolicy
from project_core.domain.retrieval.mongo_vector import MongoVectorRetriever


class SupermarketAgentService(BaseAgentService):
    """Base supermarket agent with Mongo retriever and context policy."""

    def __init__(
        self,
        config: PlatformConfig,
        spec: AgentSpec,
        *,
        skills_root: Path,
        agent_key: str,
        retriever: MongoVectorRetriever | None = None,
    ) -> None:
        super().__init__(config, spec, skills_root=skills_root)
        self.agent_key = agent_key
        self.retriever = retriever
        self.context_policy = ContextPolicy()

    def _persist(self, ctx: DecisionContext, response: AgentResponse) -> None:
        # Disable auto LTM persist — CaseStudyIndexer controls vector writes.
        return

    def build_context(self, ctx: DecisionContext, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        session = extra.get("session") if extra else None
        if session is None:
            from project_core.domain.memory.session_bundle import SessionBundle

            session = SessionBundle(session_id=ctx.request.session_id, actor_id=ctx.request.actor_id)
        return self.context_policy.build_request_context(
            self.agent_key,
            ctx.request.actor_id,
            session,
            extra=extra,
        )

    def retrieve(self, query: str, *, top_k: int = 5) -> list[Any]:
        if not self.retriever:
            return []
        return self.retriever.retrieve(query, top_k=top_k)

    def llm_system_prompt(self, *, guide: str | None = None, extra: str | None = None) -> str:
        """Assemble system prompt from SKILL.md, TOOLS.md, and task guide markdown."""
        parts: list[str] = []
        if self.skill is not None:
            parts.extend(self.skill.system_fragments())
            tools = self.skill.tool_docs()
            if tools.strip():
                parts.append(f"## Tools reference\n\n{tools}")
            if guide:
                body = self.skill.guide(guide)
                if body.strip():
                    parts.append(body)
        if extra and extra.strip():
            parts.append(extra)
        if not parts:
            return f"You are supermarket agent {self.agent_key}. Return JSON only."
        return "\n\n---\n\n".join(parts)

    @staticmethod
    def json_response(ctx: DecisionContext, payload: dict[str, Any]) -> AgentResponse:
        return AgentResponse(
            session_id=ctx.request.session_id,
            actor_id=ctx.request.actor_id,
            content=json.dumps(payload, ensure_ascii=False),
            payload=payload,
        )
