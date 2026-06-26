"""Item 8 - Context builder / management.

Decides *what* goes into the model's context window each turn: assemble
candidate fragments, then truncate / compress / summarise to fit a token budget
(avoiding "context rot"). Distinct from Memory (item 12), which is the store;
this is the per-turn windowing policy.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ContextWindow:
    """The assembled context ready to feed the model."""

    text: str
    fragments: list[str] = field(default_factory=list)
    token_estimate: int = 0
    dropped: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class ContextBuilder(ABC):
    """Assemble + fit context fragments into a window."""

    def __init__(self, *, max_tokens: int = 8000) -> None:
        self.max_tokens = max_tokens

    @abstractmethod
    def collect(self, *, goal: str, inputs: dict[str, Any], session_id: str) -> list[str]:
        """Gather candidate fragments (state, memory, retrieval, history)."""

    @abstractmethod
    def fit(self, fragments: list[str]) -> ContextWindow:
        """Truncate / compress fragments to satisfy the token budget."""

    def build(self, *, goal: str, inputs: dict[str, Any], session_id: str) -> ContextWindow:
        fragments = self.collect(goal=goal, inputs=inputs, session_id=session_id)
        return self.fit(fragments)
