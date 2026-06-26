"""Item 31 - Observability / Tracing (+ cost/token accounting).

Spans for tracing an agent/tool run, plus a token/cost accountant so spend can
be attributed per run and capped by the Budget abstraction (item 33).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class UsageRecord:
    """Token/cost usage for a single model call."""

    model_id: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Span:
    """A unit of traced work."""

    name: str
    attributes: dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any) -> None:
        self.attributes[key] = value


class Tracer(ABC):
    """Create spans around units of work."""

    @abstractmethod
    def span(self, name: str, **attributes: Any) -> AbstractContextManager[Span]: ...


class CostAccountant(ABC):
    """Record and total token/cost usage for a run."""

    @abstractmethod
    def record(self, usage: UsageRecord) -> None: ...

    @abstractmethod
    def total_cost(self) -> float: ...

    @abstractmethod
    def total_tokens(self) -> int: ...
