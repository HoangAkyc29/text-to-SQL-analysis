"""Concrete evaluator (item 5): a lightweight heuristic critic.

Scores an output on simple signals (non-empty, valid JSON if expected, presence
of required keys). Useful as a default in a :class:`ReflectionLoop` and as a
placeholder for an LLM-as-judge implementation.
"""

from __future__ import annotations

import json
from typing import Any

from agent_core.core.evaluation.base import AbstractEvaluator, EvaluationVerdict


class HeuristicEvaluator(AbstractEvaluator):
    """Cheap, deterministic output check."""

    def __init__(self, *, require_json: bool = False, required_keys: list[str] | None = None) -> None:
        self.require_json = require_json
        self.required_keys = required_keys or []

    def evaluate(self, output: str, *, context: dict[str, Any] | None = None) -> EvaluationVerdict:
        if not output.strip():
            return EvaluationVerdict(score=0.0, feedback="empty output")
        score = 0.6
        feedback = "non-empty"
        if self.require_json:
            try:
                data = json.loads(output[output.index("{") : output.rindex("}") + 1])
                score = 0.8
                missing = [k for k in self.required_keys if k not in data]
                if missing:
                    score = 0.5
                    feedback = f"missing keys: {missing}"
                else:
                    score = 1.0
                    feedback = "valid json with required keys"
            except (ValueError, json.JSONDecodeError):
                return EvaluationVerdict(score=0.3, feedback="expected JSON, none found")
        return EvaluationVerdict(score=score, feedback=feedback, passed=score >= self.threshold)
