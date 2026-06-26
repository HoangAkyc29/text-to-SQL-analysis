"""Concrete SessionStore (item 16) backed by Strands FileSessionManager."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_core.state.session_state.base import SessionState, SessionStore


class StrandsSessionStore(SessionStore):
    """Persist sessions to disk and expose a Strands SessionManager."""

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._states: dict[str, SessionState] = {}

    def load(self, session_id: str) -> SessionState:
        return self._states.setdefault(session_id, SessionState(session_id=session_id))

    def save(self, state: SessionState) -> None:
        self._states[state.session_id] = state

    def create_session_manager(self, session_id: str) -> Any:
        from strands.session.file_session_manager import FileSessionManager

        return FileSessionManager(session_id=session_id, storage_dir=str(self.storage_dir))
