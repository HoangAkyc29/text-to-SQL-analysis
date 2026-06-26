"""Item 20 - State Transition.

Explicit transition rules between named states (a finite-state machine), used to
drive deterministic phases of an agent or workflow (e.g. IDLE -> PROCESSING ->
DONE).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Transition:
    """A directed edge with an optional guard predicate."""

    source: str
    target: str
    event: str
    guard: Callable[[dict[str, Any]], bool] | None = None


class StateMachine(ABC):
    """Drive transitions between named states."""

    def __init__(self, *, initial: str, transitions: list[Transition]) -> None:
        self.state = initial
        self._transitions = transitions

    def can_fire(self, event: str, ctx: dict[str, Any]) -> Transition | None:
        for t in self._transitions:
            if t.source == self.state and t.event == event and (t.guard is None or t.guard(ctx)):
                return t
        return None

    def fire(self, event: str, ctx: dict[str, Any]) -> str:
        transition = self.can_fire(event, ctx)
        if transition is None:
            raise ValueError(f"No transition for event '{event}' from state '{self.state}'")
        self.state = transition.target
        self.on_enter(self.state, ctx)
        return self.state

    @abstractmethod
    def on_enter(self, state: str, ctx: dict[str, Any]) -> None:
        """Hook executed when a new state is entered."""
