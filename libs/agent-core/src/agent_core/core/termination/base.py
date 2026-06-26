"""Item 4 - Termination / Stopping condition.

Decides when an agent loop (or an orchestration) should stop: max iterations,
goal satisfied, budget exhausted, a stop token, etc.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class TerminationCondition(ABC):
    """Return True when the loop should stop."""

    @abstractmethod
    def should_stop(self, *, iteration: int, last_output: str) -> bool: ...


class MaxIterations(TerminationCondition):
    """Stop after a fixed number of iterations."""

    def __init__(self, limit: int) -> None:
        self.limit = limit

    def should_stop(self, *, iteration: int, last_output: str) -> bool:
        return iteration + 1 >= self.limit


class StopToken(TerminationCondition):
    """Stop when the output contains a sentinel string."""

    def __init__(self, token: str = "<DONE>") -> None:
        self.token = token

    def should_stop(self, *, iteration: int, last_output: str) -> bool:
        return self.token in last_output


class CompositeTermination(TerminationCondition):
    """Stop when ANY child condition fires."""

    def __init__(self, conditions: list[TerminationCondition]) -> None:
        self.conditions = conditions

    def should_stop(self, *, iteration: int, last_output: str) -> bool:
        return any(c.should_stop(iteration=iteration, last_output=last_output) for c in self.conditions)
