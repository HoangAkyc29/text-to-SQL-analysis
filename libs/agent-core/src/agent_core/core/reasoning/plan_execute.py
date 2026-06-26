"""Plan-and-execute: plan phase then sequential execution steps."""

from __future__ import annotations

from agent_core.core.reasoning.base import ReasoningStep, ReasoningStrategy


class PlanAndExecuteStrategy(ReasoningStrategy):
    """Phase 1 plan JSON, phase 2 execute each planned action message."""

    name = "plan_execute"

    def __init__(self, *, max_actions: int = 6) -> None:
        self.max_actions = max_actions
        self._planned: list[str] = []

    def next_step(self, goal: str, trace: list[ReasoningStep]) -> ReasoningStep:
        if not self._planned and not trace:
            message = (
                f"Create a JSON plan to achieve: {goal}\n"
                'Return {"steps":["step1","step2",...]} with at most '
                f"{self.max_actions} steps."
            )
            return ReasoningStep(thought="planning", action={"message": message, "phase": "plan"})

        if not self._planned and trace:
            self._planned = self._parse_plan(trace[-1].observation or trace[-1].thought)

        if self._planned:
            nxt = self._planned.pop(0)
            return ReasoningStep(
                thought=f"execute: {nxt}",
                action={"message": nxt, "phase": "execute"},
            )
        return ReasoningStep(thought="done", action=None)

    def is_complete(self, trace: list[ReasoningStep]) -> bool:
        if trace and trace[-1].action is None:
            return True
        return not self._planned and bool(trace) and trace[-1].metadata.get("phase") == "execute"

    @staticmethod
    def _parse_plan(text: str) -> list[str]:
        import json

        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            data = json.loads(text[start:end])
            steps = data.get("steps", [])
            return [str(s) for s in steps]
        except (ValueError, json.JSONDecodeError):
            return [text.strip()] if text.strip() else []
