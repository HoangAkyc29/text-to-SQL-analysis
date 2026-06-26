"""Item 16 - Conversation / Session State.

The durable handle for one conversation/session: id, turns, and arbitrary
session-scoped values. A SessionStore creates/loads sessions (this is the seam
that a Strands ``SessionManager`` plugs into).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SessionState:
    """In-memory view of a conversation session."""

    session_id: str
    actor_id: str = "anonymous"
    turns: list[dict[str, Any]] = field(default_factory=list)
    values: dict[str, Any] = field(default_factory=dict)


class SessionStore(ABC):
    """Create / load / persist conversation sessions."""

    @abstractmethod
    def load(self, session_id: str) -> SessionState: ...

    @abstractmethod
    def save(self, state: SessionState) -> None: ...

    @abstractmethod
    def create_session_manager(self, session_id: str) -> Any:
        """Return the framework session manager (e.g. a Strands SessionManager)."""
