"""Item 23 - Result aggregation / Synthesis.

Combine outputs from multiple agents/tasks: voting, merge, map-reduce, or a
supervisor LLM that synthesises a final answer.

    aggregate(results) -> final
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ResultAggregator(ABC):
    """Reduce many partial results into one."""

    @abstractmethod
    def aggregate(self, results: list[Any], *, context: dict[str, Any] | None = None) -> Any:
        """Combine ``results`` into a single output."""


class MajorityVote(ResultAggregator):
    """Pick the most common result (simple consensus)."""

    def aggregate(self, results: list[Any], *, context: dict[str, Any] | None = None) -> Any:
        if not results:
            return None
        counts: dict[Any, int] = {}
        for r in results:
            counts[r] = counts.get(r, 0) + 1
        return max(counts.items(), key=lambda kv: kv[1])[0]


class ConcatMerge(ResultAggregator):
    """Concatenate textual results with a separator."""

    def __init__(self, separator: str = "\n\n") -> None:
        self.separator = separator

    def aggregate(self, results: list[Any], *, context: dict[str, Any] | None = None) -> str:
        return self.separator.join(str(r) for r in results)
