"""BaseAgentService - the integration layer.

This is where the abstractions stop being theoretical and get wired into a real
agent. One ``run(AgentRequest) -> AgentResponse`` call:

  1. opens/loads the session (STM, item 12 / 16)
  2. recalls long-term memory (LTM, item 12)
  3. loads the skill bundle: SKILL.md + TOOLS.md + prompts (items 7/9)
  4. builds the context window (item 8) from skill docs + LTM + STM + inbox
  5. resolves + connects this agent's MCP servers from the central registry
     (items 48/49) and namespaces their tools via the adapter (item 50)
  6. delegates the domain decision to ``decide`` (subclass)
  7. persists results to LTM + a checkpoint (item 19) and appends to STM

Subclasses implement ``decide`` only.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from commons.logging import get_logger

from agent_core.capabilities.context.default_builder import DefaultContextBuilder
from agent_core.capabilities.memory.base import MemoryRecord
from agent_core.capabilities.models.openai_compatible import OpenAICompatibleProvider
from agent_core.core.persona.base import Persona
from agent_core.core.reasoning.factory import build_reasoning
from agent_core.core.reasoning.loop import ReasoningLoop
from agent_core.io.schemas import AgentRequest, AgentResponse
from agent_core.skills.bundle import SkillBundle
from agent_core.state.agent_state.in_memory import InMemoryAgentState
from agent_core.state.persistence.base import Checkpoint
from agent_core.state.persistence.sqlite_checkpoint import SQLiteCheckpointStore
from agent_core.state.session_state.strands_session import StrandsSessionStore
from mcp_core.client.adapter.strands_adapter import StrandsMCPAgentAdapter
from mcp_core.client.registry.strands_registry import StrandsMCPServerRegistry

from platform_core.config.schema import AgentSpec, PlatformConfig
from platform_core.infra.backends import build_platform_backends
from platform_core.registry.mcp_registry import PlatformMCPRegistry

log = get_logger("platform_core.service")


@dataclass
class DecisionContext:
    """Everything ``decide`` needs for one turn."""

    request: AgentRequest
    tools: list[Any]
    mcp: StrandsMCPServerRegistry
    context_text: str
    system_prompt: str


class BaseAgentService(ABC):
    """Common scaffolding shared by every agent service."""

    def __init__(
        self,
        config: PlatformConfig,
        spec: AgentSpec,
        *,
        skills_root: Path,
        persona: Persona | None = None,
    ) -> None:
        self.config = config
        self.spec = spec
        self.persona = persona
        self.model_provider = OpenAICompatibleProvider()
        self.adapter = StrandsMCPAgentAdapter()
        self.reasoning = build_reasoning(spec.reasoning)

        self.mcp_registry = PlatformMCPRegistry(config)
        self.endpoints = self.mcp_registry.endpoints_for(spec.mcp_servers)

        self.skill: SkillBundle | None = None
        if spec.skill:
            self.skill = SkillBundle.load(skills_root, spec.skill)

        backends = build_platform_backends(config)
        self.stm = backends["stm"]
        self.ltm = backends["ltm"]
        self.retriever = backends["retriever"]
        self.cache = backends["cache"]

        mem = config.memory
        if hasattr(self.stm, "create_session_manager"):
            self.sessions = self.stm  # type: ignore[assignment]
        else:
            self.sessions = StrandsSessionStore(config.resolve_path(mem.stm_dir))
        self.checkpoints = SQLiteCheckpointStore(config.resolve_path(mem.checkpoint_db_path))
        self.state = InMemoryAgentState()

    @abstractmethod
    def decide(self, ctx: DecisionContext) -> AgentResponse:
        """Domain logic: produce the AgentResponse (content + structured payload)."""

    def has_llm(self) -> bool:
        import os

        return bool(
            os.getenv("OPENROUTER_API_KEY")
            or os.getenv("openroute_api_key")
            or os.getenv("OPENAI_API_KEY")
        )

    def run_strands(
        self,
        system_prompt: str,
        message: str,
        tools: list[Any],
        session_id: str,
        *,
        reasoning: Any = None,
    ) -> str:
        """Run a single Strands agent turn with optional reasoning loop."""
        strategy = reasoning or self.reasoning

        def _invoke(msg: str) -> str:
            from strands import Agent as StrandsAgent

            session_mgr = self.sessions.create_session_manager(session_id)

            agent = StrandsAgent(
                model=self.model_provider.create(),
                system_prompt=system_prompt,
                tools=tools,
                session_manager=session_mgr,
            )
            result = agent(msg)
            return str(getattr(result, "content", result))

        if strategy is not None:
            text, _trace = ReasoningLoop(strategy).run(message, _invoke)
            return text
        return _invoke(message)

    def build_system_prompt(self, ltm_context: str | None) -> str:
        parts: list[str] = []
        if self.persona is not None:
            parts.append(self.persona.to_system_prompt())
        if self.skill is not None:
            parts.extend(self.skill.system_fragments())
        if ltm_context:
            parts.append(ltm_context)
        return "\n\n".join(p for p in parts if p.strip())

    def run(self, request: AgentRequest) -> AgentResponse:
        session_id = request.session_id or f"sess-{uuid4().hex[:8]}"
        self.stm.append(session_id, "user", request.message)

        ltm_records = self.ltm.retrieve(request.actor_id, query=request.message, limit=5)
        ltm_fragments = [f"[{r.namespace}] {r.content}" for r in ltm_records]

        retrieval_fragments: list[str] = []
        if self.retriever is not None:
            chunks = self.retriever.retrieve(request.message, top_k=self.config.memory.retrieval.top_k)
            retrieval_fragments = [f"({c.score:.2f}) {c.text}" for c in chunks]

        ltm_context = ("Known long-term context:\n" + "\n".join(ltm_fragments)) if ltm_fragments else None

        builder = DefaultContextBuilder(
            skill_docs=self.skill.tool_docs() if self.skill else "",
            ltm_fragments=ltm_fragments,
            retrieval_fragments=retrieval_fragments,
            stm_history=self.stm.history(session_id),
            state_snapshot=dict(request.metadata),
        )
        window = builder.build(goal=request.message, inputs=request.inbox, session_id=session_id)
        system_prompt = self.build_system_prompt(ltm_context)

        registry = StrandsMCPServerRegistry()
        for ep in self.endpoints:
            registry.add(ep)

        if self.endpoints:
            with registry:
                tools = registry.adapted_tools(self.adapter)
                response = self.decide(
                    DecisionContext(
                        request=request,
                        tools=tools,
                        mcp=registry,
                        context_text=window.text,
                        system_prompt=system_prompt,
                    )
                )
        else:
            response = self.decide(
                DecisionContext(
                    request=request,
                    tools=[],
                    mcp=registry,
                    context_text=window.text,
                    system_prompt=system_prompt,
                )
            )

        response.session_id = session_id
        response.actor_id = request.actor_id
        self._persist(request, session_id, response)
        return response

    def _persist(self, request: AgentRequest, session_id: str, response: AgentResponse) -> None:
        self.stm.append(session_id, "assistant", response.content or "")
        record = MemoryRecord(
            content=f"{self.spec.name}: {response.content[:500]}",
            actor_id=request.actor_id,
            namespace=self.spec.name,
        )
        self.ltm.store(request.actor_id, record)
        response.memory_refs.append(record.id)
        self.checkpoints.save(
            Checkpoint(
                checkpoint_id=f"{session_id}:{self.spec.name}",
                scope=f"agent:{self.spec.name}",
                payload={"payload": response.payload, "metadata": dict(request.metadata)},
            )
        )
