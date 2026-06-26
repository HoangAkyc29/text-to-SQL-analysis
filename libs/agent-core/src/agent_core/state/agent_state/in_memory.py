"""Concrete internal agent state (item 14)."""

from __future__ import annotations

from typing import Any

from agent_core.state.agent_state.base import AgentState


class InMemoryAgentState(AgentState):
    """Dict-backed internal state for a single agent instance."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def snapshot(self) -> dict[str, Any]:
        return dict(self._data)

    def restore(self, snapshot: dict[str, Any]) -> None:
        self._data = dict(snapshot)
