"""Item 33 - Budget / Rate limit / Resource governance.

Caps on tokens, cost, tool calls and concurrency. The guard is consulted before
expensive operations and raises / signals when a ceiling is hit.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class BudgetLimits:
    max_tokens: int | None = None
    max_cost_usd: float | None = None
    max_tool_calls: int | None = None
    max_concurrency: int | None = None


class BudgetExceeded(Exception):
    """Raised when a budget ceiling is reached."""


class BudgetGuard(ABC):
    """Track consumption against limits and gate further work."""

    def __init__(self, limits: BudgetLimits) -> None:
        self.limits = limits

    @abstractmethod
    def charge(self, *, tokens: int = 0, cost_usd: float = 0.0, tool_calls: int = 0) -> None:
        """Record consumption; raise :class:`BudgetExceeded` if over limit."""

    @abstractmethod
    def remaining(self) -> BudgetLimits:
        """Return the remaining headroom."""
