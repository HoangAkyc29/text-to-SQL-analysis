"""Item 5 - Evaluator / Critic / Reflection.

Self-scoring of an agent's output. Supports LLM-as-judge and a reflection loop
that re-runs a producer until the score passes a threshold.

    evaluate(output) -> EvaluationVerdict(score, feedback)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class EvaluationVerdict:
    """Outcome of an evaluation."""

    score: float  # normalised 0..1
    feedback: str = ""
    passed: bool = False
    details: dict[str, Any] = field(default_factory=dict)


class AbstractEvaluator(ABC):
    """Score an output, optionally against a reference / context."""

    threshold: float = 0.7

    @abstractmethod
    def evaluate(self, output: str, *, context: dict[str, Any] | None = None) -> EvaluationVerdict:
        """Return a verdict for ``output``."""

    def is_acceptable(self, verdict: EvaluationVerdict) -> bool:
        return verdict.score >= self.threshold


class ReflectionLoop:
    """Generic produce -> evaluate -> refine loop.

    ``producer`` returns text; ``evaluator`` scores it. If the score is below the
    threshold, ``producer`` is called again with the feedback until it passes or
    ``max_rounds`` is reached.
    """

    def __init__(self, evaluator: AbstractEvaluator, *, max_rounds: int = 3) -> None:
        self.evaluator = evaluator
        self.max_rounds = max_rounds

    def run(
        self,
        producer: Callable[[str | None], str],
        *,
        context: dict[str, Any] | None = None,
    ) -> tuple[str, EvaluationVerdict]:
        feedback: str | None = None
        output = producer(None)
        verdict = self.evaluator.evaluate(output, context=context)
        rounds = 1
        while not self.evaluator.is_acceptable(verdict) and rounds < self.max_rounds:
            feedback = verdict.feedback
            output = producer(feedback)
            verdict = self.evaluator.evaluate(output, context=context)
            rounds += 1
        verdict.passed = self.evaluator.is_acceptable(verdict)
        return output, verdict
