"""In-memory blackboard backed by an optional :class:`StateSchema`."""

from __future__ import annotations

from typing import Any

from agent_core.state.schema.base import StateSchema
from agent_core.state.shared_state.base import Blackboard


class InMemoryBlackboard(Blackboard):
    """Thread-unsafe in-process blackboard for graph shared state."""

    def __init__(
        self,
        *,
        initial: dict[str, Any] | None = None,
        schema: StateSchema | None = None,
    ) -> None:
        self._data: dict[str, Any] = dict(initial or {})
        self._schema = schema

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    def read(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def write(self, key: str, value: Any, *, author: str = "") -> None:
        if self._schema is not None:
            self._data = self._schema.apply(self._data, {key: value})
        else:
            self._data[key] = value

    def apply_updates(self, updates: dict[str, Any]) -> dict[str, Any]:
        """Merge *updates* via schema (if any) and return the new snapshot."""
        if self._schema is not None:
            self._data = self._schema.apply(self._data, updates)
        else:
            self._data.update(updates)
        return dict(self._data)

    def snapshot(self) -> dict[str, Any]:
        return dict(self._data)

    def keys(self, *, prefix: str = "") -> list[str]:
        return [k for k in self._data if k.startswith(prefix)]
