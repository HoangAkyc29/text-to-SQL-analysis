"""Pydantic schema for ``platform.yaml`` - the single source of truth.

Everything about who exists and how they connect lives here so the rest of the
system never hardcodes a connection.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from agent_core.infra.backends.config import (
    CacheBackendConfig,
    CommunicationConfig,
    LTMBackendConfig,
    RetrievalBackendConfig,
    STMBackendConfig,
)
from agent_core.multiagent.orchestration.graph import (
    ConditionalRoute,
    ExecutionPlan,
    GraphEdgeSpec,
    GraphNodeSpec,
    build_plan,
)
from agent_core.state.schema.base import AppendReducer, LastWriteWins, StateChannel, StateSchema


class MCPServerAuthSpec(BaseModel):
    mode: str = "none"  # none | bearer | jwt | composite
    token_env: str | None = None
    jwt_secret_env: str | None = None
    scopes: dict[str, list[str]] = Field(default_factory=dict)


class MCPServerSpec(BaseModel):
    """One MCP server entry."""

    name: str
    prefix: str
    transport: str = "stdio"
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    url_env: str | None = None
    url: str | None = None
    tool_filters: list[str] = Field(default_factory=list)
    auth: MCPServerAuthSpec | None = None


class AgentSpec(BaseModel):
    """One agent entry."""

    name: str
    capabilities: list[str] = Field(default_factory=list)
    factory: str
    endpoint_env: str | None = None
    endpoint: str | None = None
    mcp_servers: list[str] = Field(default_factory=list)
    skill: str | None = None
    reasoning: str | None = None
    auth_token_env: str | None = None
    tls_verify: bool = True


class GraphEdge(BaseModel):
    from_: str = Field(alias="from")
    to: str
    when: str | None = None

    model_config = {"populate_by_name": True}


class ConditionalRouteSpec(BaseModel):
    """One branch in a conditional node."""

    to: str | None = None
    when: str | None = None
    else_: str | None = Field(default=None, alias="else")

    model_config = {"populate_by_name": True}


class GraphNodeSpecModel(BaseModel):
    """Extended node behaviour (parallel, conditional, join, debate)."""

    type: str = "agent"  # agent | parallel | conditional | join | debate
    agents: list[str] = Field(default_factory=list)
    merge: str = "concat"
    routes: list[ConditionalRouteSpec] = Field(default_factory=list)
    state_map: dict[str, str] = Field(default_factory=dict)
    participants: list[str] = Field(default_factory=list)
    facilitator: str | None = None
    max_rounds: int = 1
    rotation: str = "alternating"
    transcript_channel: str = "debate_transcript"
    output_channel: str | None = None


class StateChannelSpecModel(BaseModel):
    reducer: str = "last_write"  # last_write | append


class OrchestrationStateConfig(BaseModel):
    channels: dict[str, StateChannelSpecModel] = Field(default_factory=dict)


def build_state_schema(state: OrchestrationStateConfig | None) -> StateSchema | None:
    if state is None or not state.channels:
        return None
    schema = StateSchema()
    for name, ch in state.channels.items():
        if ch.reducer == "append":
            schema.add(StateChannel(name=name, reducer=AppendReducer(), default=[]))
        else:
            schema.add(StateChannel(name=name, reducer=LastWriteWins()))
    return schema


class OrchestrationConfig(BaseModel):
    """How agents are composed."""

    type: str = "graph"  # graph | sequential
    entry: str | None = None
    runtime: str = "sync"  # sync | thread_pool
    max_workers: int = 4
    graph: list[GraphEdge] = Field(default_factory=list)
    nodes: dict[str, GraphNodeSpecModel] = Field(default_factory=dict)
    state: OrchestrationStateConfig | None = None

    def order(self) -> list[str]:
        """Backward-compatible linear order for simple chains (no cycle validation)."""
        if not self.graph:
            return [self.entry] if self.entry else []
        nxt = {e.from_: e.to for e in self.graph if e.when is None}
        start = self.entry or self.graph[0].from_
        order = [start]
        cur = start
        seen = {start}
        while cur in nxt and nxt[cur] not in seen:
            cur = nxt[cur]
            order.append(cur)
            seen.add(cur)
        return order

    def to_execution_plan(self) -> ExecutionPlan:
        """Build a framework-neutral execution plan from this config."""
        if not self.graph and not self.entry:
            raise ValueError("orchestration.graph/entry is empty")
        entry = self.entry or (self.graph[0].from_ if self.graph else "")
        edges = [GraphEdgeSpec(source=e.from_, target=e.to, when=e.when) for e in self.graph]
        nodes: dict[str, GraphNodeSpec] = {}
        for name, spec in self.nodes.items():
            routes: list[ConditionalRoute] = []
            for r in spec.routes:
                if r.else_ is not None:
                    routes.append(ConditionalRoute(target=r.else_, when=None))
                elif r.to is not None:
                    routes.append(ConditionalRoute(target=r.to, when=r.when))
            nodes[name] = GraphNodeSpec(
                id=name,
                kind=spec.type,  # type: ignore[arg-type]
                agents=list(spec.agents),
                merge=spec.merge,  # type: ignore[arg-type]
                routes=routes,
                state_map=dict(spec.state_map),
                participants=list(spec.participants),
                facilitator=spec.facilitator,
                max_rounds=spec.max_rounds,
                rotation=spec.rotation,  # type: ignore[arg-type]
                transcript_channel=spec.transcript_channel,
                output_channel=spec.output_channel,
            )
        return build_plan(
            entry=entry,
            edges=edges,
            nodes=nodes,
            state_schema=build_state_schema(self.state),
        )


class MemoryConfig(BaseModel):
    """Shared memory/state backends (legacy flat fields + nested overrides)."""

    stm_dir: str = "./data/stm"
    ltm_backend: str = "sqlite"
    ltm_db_path: str = "./data/ltm.db"
    checkpoint_db_path: str = "./data/checkpoints.db"
    stm: STMBackendConfig | None = None
    ltm: LTMBackendConfig | None = None
    retrieval: RetrievalBackendConfig = Field(default_factory=RetrievalBackendConfig)

    def resolved_stm(self) -> STMBackendConfig:
        if self.stm is not None:
            return self.stm
        return STMBackendConfig(backend="in_memory", dir=self.stm_dir)

    def resolved_ltm(self) -> LTMBackendConfig:
        if self.ltm is not None:
            return self.ltm
        return LTMBackendConfig(backend=self.ltm_backend, db_path=self.ltm_db_path)


class PromptsConfig(BaseModel):
    """Where skill bundles / prompts live, relative to each agent package."""

    skills_dirname: str = "skills"


class PlatformConfig(BaseModel):
    """Root config object."""

    mcp_servers: dict[str, MCPServerSpec] = Field(default_factory=dict)
    agents: dict[str, AgentSpec] = Field(default_factory=dict)
    orchestration: OrchestrationConfig = Field(default_factory=OrchestrationConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    cache: CacheBackendConfig = Field(default_factory=CacheBackendConfig)
    communication: CommunicationConfig = Field(default_factory=CommunicationConfig)
    prompts: PromptsConfig = Field(default_factory=PromptsConfig)
    require_https: bool = False

    base_dir: Path = Field(default_factory=Path.cwd)

    def resolve_path(self, value: str) -> Path:
        p = Path(value)
        return p if p.is_absolute() else (self.base_dir / p)

    def agent_by_capability(self, capability: str) -> AgentSpec | None:
        for spec in self.agents.values():
            if capability in spec.capabilities:
                return spec
        return None
