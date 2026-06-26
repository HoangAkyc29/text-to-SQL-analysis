"""Default reasoning: single Strands delegation (current behaviour)."""

from __future__ import annotations

from typing import Any

from agent_core.core.reasoning.base import ReasoningStep, ReasoningStrategy


class PassthroughStrategy(ReasoningStrategy):
    """One step: pass the goal through to the model executor."""

    name = "passthrough"

    def next_step(self, goal: str, trace: list[ReasoningStep]) -> ReasoningStep:
        return ReasoningStep(thought="delegate to model", action={"message": goal})

    def is_complete(self, trace: list[ReasoningStep]) -> bool:
        return bool(trace)
