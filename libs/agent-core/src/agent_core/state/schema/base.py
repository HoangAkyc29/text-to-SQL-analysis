"""Item 18 - State Schema / Reducer.

Declares the shape of state and how concurrent updates to each field are merged
(LangGraph-style channels + reducers). Example reducers: last-write-wins, append
to list, numeric add, set-union.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

V = TypeVar("V")


class Reducer(ABC, Generic[V]):
    """Merge a new value into the existing channel value."""

    @abstractmethod
    def reduce(self, current: V | None, update: V) -> V: ...


class LastWriteWins(Reducer[Any]):
    def reduce(self, current: Any, update: Any) -> Any:
        return update


class AppendReducer(Reducer[list]):
    def reduce(self, current: list | None, update: list) -> list:
        return [*(current or []), *update]


@dataclass(slots=True)
class StateChannel:
    """A named field with its merge policy."""

    name: str
    reducer: Reducer[Any]
    default: Any = None


@dataclass(slots=True)
class StateSchema:
    """A set of channels describing a state object."""

    channels: dict[str, StateChannel] = field(default_factory=dict)

    def add(self, channel: StateChannel) -> "StateSchema":
        self.channels[channel.name] = channel
        return self

    def apply(self, state: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
        """Apply ``updates`` to ``state`` using each channel's reducer."""
        out = dict(state)
        for key, value in updates.items():
            channel = self.channels.get(key)
            if channel is None:
                out[key] = value
            else:
                out[key] = channel.reducer.reduce(out.get(key, channel.default), value)
        return out
