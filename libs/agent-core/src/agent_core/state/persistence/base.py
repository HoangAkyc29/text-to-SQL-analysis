"""Item 19 - Persistence / Checkpointing.

Save and restore state snapshots so a workflow/agent can resume after a crash or
a human-in-the-loop pause.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class Checkpoint:
    """A point-in-time snapshot of some state."""

    checkpoint_id: str
    scope: str  # e.g. "workflow:<id>" or "agent:<name>"
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CheckpointStore(ABC):
    """Persist / load checkpoints."""

    @abstractmethod
    def save(self, checkpoint: Checkpoint) -> None: ...

    @abstractmethod
    def latest(self, scope: str) -> Checkpoint | None: ...

    @abstractmethod
    def load(self, checkpoint_id: str) -> Checkpoint | None: ...
