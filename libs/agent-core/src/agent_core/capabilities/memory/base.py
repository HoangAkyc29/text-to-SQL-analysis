"""Item 12 - Memory (short-term + long-term).

Storage of conversational / experiential data. Short-term memory is the working
session transcript; long-term memory persists durable records across sessions.
This is the *store*; deciding what enters the window each turn is the
ContextBuilder (item 8); semantic recall is the Retriever (item 13).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class MemoryRecord:
    """A single long-term memory entry."""

    content: str
    actor_id: str = ""
    namespace: str = "facts"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


class ShortTermMemory(ABC):
    """Working memory for a single session (turn-by-turn transcript)."""

    @abstractmethod
    def append(self, session_id: str, role: str, content: str) -> None: ...

    @abstractmethod
    def history(self, session_id: str, *, limit: int | None = None) -> list[dict[str, str]]: ...

    @abstractmethod
    def reset(self, session_id: str) -> None: ...


class LongTermMemory(ABC):
    """Durable memory across sessions."""

    @abstractmethod
    def store(self, actor_id: str, record: MemoryRecord) -> None: ...

    @abstractmethod
    def retrieve(self, actor_id: str, *, query: str | None = None, limit: int = 10) -> list[MemoryRecord]: ...

    def retrieve_semantic(self, actor_id: str, *, query: str, top_k: int = 5) -> list[MemoryRecord]:
        """Semantic recall; default falls back to keyword :meth:`retrieve`."""
        return self.retrieve(actor_id, query=query, limit=top_k)
