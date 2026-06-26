"""Chain-of-thought prompting strategy."""

from __future__ import annotations

from agent_core.core.reasoning.base import ReasoningStep, ReasoningStrategy


class ChainOfThoughtStrategy(ReasoningStrategy):
    """Inject CoT instructions; single model call with explicit reasoning trace request."""

    name = "cot"

    def __init__(self, *, prefix: str = "Think step by step before answering.") -> None:
        self.prefix = prefix

    def next_step(self, goal: str, trace: list[ReasoningStep]) -> ReasoningStep:
        message = f"{self.prefix}\n\nGoal: {goal}\n\nProvide your reasoning, then the final answer."
        return ReasoningStep(thought="chain-of-thought prompt", action={"message": message})

    def is_complete(self, trace: list[ReasoningStep]) -> bool:
        return bool(trace)
