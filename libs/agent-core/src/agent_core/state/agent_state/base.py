"""Item 14 - Agent State (internal).

Private, per-agent scratch state: current goal, scratchpad, counters, last tool
results. Not shared with other agents (that is the blackboard, item 15).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AgentState(ABC):
    """Key-value internal state for a single agent instance."""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any: ...

    @abstractmethod
    def set(self, key: str, value: Any) -> None: ...

    @abstractmethod
    def snapshot(self) -> dict[str, Any]:
        """Return a serialisable copy of the full state."""

    @abstractmethod
    def restore(self, snapshot: dict[str, Any]) -> None:
        """Replace state from a snapshot (used by checkpointing, item 19)."""
