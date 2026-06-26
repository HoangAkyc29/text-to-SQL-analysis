"""Item 44 - Session / Connection.

Manage multiple concurrent client connections, each with its own per-session
state (negotiated capabilities, auth principal, scratch data).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ServerSession:
    """Per-connection server-side state."""

    session_id: str
    principal: str | None = None
    capabilities: dict[str, Any] = field(default_factory=dict)
    values: dict[str, Any] = field(default_factory=dict)


class SessionManager(ABC):
    """Create / fetch / drop client sessions."""

    @abstractmethod
    def open(self, session_id: str, *, principal: str | None = None) -> ServerSession: ...

    @abstractmethod
    def get(self, session_id: str) -> ServerSession | None: ...

    @abstractmethod
    def close(self, session_id: str) -> None: ...
