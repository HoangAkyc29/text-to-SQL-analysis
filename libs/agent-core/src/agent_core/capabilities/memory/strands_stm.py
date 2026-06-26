"""Concrete short-term memory (item 12 STM).

Two faces of STM:
  - ``InMemoryShortTermMemory``: a simple per-session transcript (good default).
  - ``StrandsSTM``: a thin wrapper that produces a Strands ``FileSessionManager``
    so the underlying Strands Agent persists its own conversation per session.

The two are complementary: the Strands session manager handles the model's view
of the conversation, while the transcript is convenient for context building.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_core.capabilities.memory.base import ShortTermMemory


class InMemoryShortTermMemory(ShortTermMemory):
    """Process-local per-session transcript."""

    def __init__(self) -> None:
        self._sessions: dict[str, list[dict[str, str]]] = {}

    def append(self, session_id: str, role: str, content: str) -> None:
        self._sessions.setdefault(session_id, []).append({"role": role, "content": content})

    def history(self, session_id: str, *, limit: int | None = None) -> list[dict[str, str]]:
        turns = self._sessions.get(session_id, [])
        return turns[-limit:] if limit else list(turns)

    def reset(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


class StrandsSTM:
    """Factory for Strands ``FileSessionManager`` instances (file-backed STM)."""

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def create_session_manager(self, session_id: str) -> Any:
        from strands.session.file_session_manager import FileSessionManager

        return FileSessionManager(session_id=session_id, storage_dir=str(self.storage_dir))
