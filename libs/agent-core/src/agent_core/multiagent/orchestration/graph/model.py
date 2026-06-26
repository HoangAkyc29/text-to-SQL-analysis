"""Graph orchestration data models (framework-neutral)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from agent_core.state.schema.base import StateSchema
from agent_core.state.workflow_state.base import WorkflowState


NodeKind = Literal["agent", "parallel", "conditional", "join", "debate"]
MergeStrategy = Literal["concat", "majority_vote", "last", "state_map"]
DebateRotation = Literal["alternating", "round_robin"]


@dataclass(slots=True)
class GraphEdgeSpec:
    """Directed edge with an optional condition expression."""

    source: str
    target: str
    when: str | None = None


@dataclass(slots=True)
class ConditionalRoute:
    """One branch of a conditional node."""

    target: str
    when: str | None = None  # None means catch-all ``else``


@dataclass(slots=True)
class GraphNodeSpec:
    """Behaviour override for a node id (parallel, conditional, join, debate)."""

    id: str
    kind: NodeKind = "agent"
    agents: list[str] = field(default_factory=list)
    merge: MergeStrategy = "concat"
    routes: list[ConditionalRoute] = field(default_factory=list)
    state_map: dict[str, str] = field(default_factory=dict)
    participants: list[str] = field(default_factory=list)
    facilitator: str | None = None
    max_rounds: int = 1
    rotation: DebateRotation = "alternating"
    transcript_channel: str = "debate_transcript"
    output_channel: str | None = None


@dataclass(slots=True)
class ExecutionPlan:
    """Validated graph ready for execution."""

    entry: str
    edges: list[GraphEdgeSpec]
    nodes: dict[str, GraphNodeSpec]
    all_node_ids: set[str]
    state_schema: StateSchema | None = None


@dataclass(slots=True)
class GraphRunResult:
    """Outcome of a graph execution."""

    goal: str
    inputs: dict[str, Any]
    order: list[str]
    execution_levels: list[list[str]]
    node_outputs: dict[str, Any]
    skipped_nodes: list[str]
    parallel_groups: list[list[str]]
    final: Any
    final_content: str = ""
    shared_state: dict[str, Any] = field(default_factory=dict)
    workflow: WorkflowState | None = None
