"""ReAct-style reasoning loop (thought -> action placeholders)."""

from __future__ import annotations

from typing import Any

from agent_core.core.reasoning.base import ReasoningStep, ReasoningStrategy


class ReActStrategy(ReasoningStrategy):
    """Iterative thought/action/observation steps until complete or max_steps."""

    name = "react"

    def __init__(self, *, max_steps: int = 5) -> None:
        self.max_steps = max_steps

    def next_step(self, goal: str, trace: list[ReasoningStep]) -> ReasoningStep:
        step_no = len(trace) + 1
        prior = ""
        if trace:
            last = trace[-1]
            prior = f"\nPrior observation: {last.observation or last.thought}"
        message = (
            f"ReAct step {step_no}/{self.max_steps} for goal: {goal}{prior}\n"
            "Respond with THOUGHT and optional ACTION as JSON "
            '{"thought":"...","action":null} when done set action null.'
        )
        return ReasoningStep(thought=f"react-step-{step_no}", action={"message": message})

    def is_complete(self, trace: list[ReasoningStep]) -> bool:
        if len(trace) >= self.max_steps:
            return True
        if trace and trace[-1].action is None:
            return True
        return False

    def record_observation(self, trace: list[ReasoningStep], observation: str) -> None:
        if trace:
            trace[-1].observation = observation
