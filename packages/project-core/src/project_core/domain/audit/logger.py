from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4


class AuditLogger:
    def __init__(self, sink: list[dict[str, Any]] | None = None) -> None:
        self._events = sink if sink is not None else []

    def log(self, event_type: str, *, trace_id: str | None = None, payload: dict[str, Any] | None = None) -> None:
        self._events.append(
            {
                "event_id": str(uuid4()),
                "event_type": event_type,
                "trace_id": trace_id,
                "payload": payload or {},
                "at": datetime.utcnow().isoformat(),
            }
        )

    def events(self) -> list[dict[str, Any]]:
        return list(self._events)
