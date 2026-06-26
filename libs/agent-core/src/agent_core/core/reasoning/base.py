"""Item 3 - Reasoning / Planning strategy (within a single agent).

Strategies decide *how* an agent thinks before acting: ReAct, plan-and-execute,
chain-of-thought, tree-of-thought, etc. This is intra-agent planning, distinct
from system-level task decomposition (item 22).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ReasoningStep:
    """One unit of a reasoning trace."""

    thought: str
    action: dict[str, Any] | None = None
    observation: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ReasoningStrategy(ABC):
    """Produce the next reasoning step(s) given the current trace."""

    name: str = "reasoning"

    @abstractmethod
    def next_step(self, goal: str, trace: list[ReasoningStep]) -> ReasoningStep:
        """Return the next reasoning step toward ``goal``."""

    def is_complete(self, trace: list[ReasoningStep]) -> bool:
        """Whether the strategy considers reasoning finished. Override as needed."""
        return bool(trace) and trace[-1].action is None
