"""Drive a :class:`ReasoningStrategy` loop against a model executor."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from agent_core.core.reasoning.base import ReasoningStep, ReasoningStrategy


class ReasoningLoop:
    """Run strategy steps until complete, calling *executor* per action."""

    def __init__(self, strategy: ReasoningStrategy) -> None:
        self.strategy = strategy

    def run(
        self,
        goal: str,
        executor: Callable[[str], str],
        *,
        max_iterations: int = 8,
    ) -> tuple[str, list[ReasoningStep]]:
        trace: list[ReasoningStep] = []
        last_output = ""

        for _ in range(max_iterations):
            if self.strategy.is_complete(trace):
                break
            step = self.strategy.next_step(goal, trace)
            trace.append(step)
            if step.action is None:
                break
            message = str(step.action.get("message", goal))
            last_output = executor(message)
            step.observation = last_output
            if hasattr(self.strategy, "record_observation"):
                self.strategy.record_observation(trace, last_output)  # type: ignore[attr-defined]

        return last_output, trace
