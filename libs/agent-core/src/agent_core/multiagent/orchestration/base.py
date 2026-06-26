"""Item 25 - Orchestration / Coordination.

Defines *how* agents are composed: sequential, parallel, hierarchical
(supervisor), or graph. This is the coordination topology; the Runtime (item 28)
decides the execution mechanics (threads, async, workers).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentNode:
    """A node in an orchestration graph: a callable agent + routing metadata."""

    name: str
    run: Callable[[dict[str, Any]], Any]
    next_nodes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OrchestrationResult:
    """Outcome of running an orchestration."""

    output: Any
    node_outputs: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class Orchestrator(ABC):
    """Coordinate a set of agent nodes toward a goal."""

    def __init__(self, nodes: list[AgentNode]) -> None:
        self.nodes = {n.name: n for n in nodes}

    @abstractmethod
    def run(self, goal: str, *, inputs: dict[str, Any] | None = None) -> OrchestrationResult:
        """Execute the orchestration and return the aggregated result."""


class SequentialOrchestrator(Orchestrator):
    """Run nodes in declaration order, threading each output into the next."""

    def __init__(self, nodes: list[AgentNode]) -> None:
        super().__init__(nodes)
        self._order = [n.name for n in nodes]

    def run(self, goal: str, *, inputs: dict[str, Any] | None = None) -> OrchestrationResult:
        ctx: dict[str, Any] = {"goal": goal, **(inputs or {})}
        outputs: dict[str, Any] = {}
        last: Any = None
        for name in self._order:
            last = self.nodes[name].run(ctx)
            outputs[name] = last
            ctx[f"{name}_output"] = last
        return OrchestrationResult(output=last, node_outputs=outputs)
