"""Item 27 - Event bus / Pub-sub.

Event-driven coordination: agents publish events and subscribe to topics instead
of calling each other directly. Concrete impls can be in-memory or backed by
Redis / a message broker.

    publish(event)
    subscribe(topic, handler)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

EventHandler = Callable[["Event"], None]


@dataclass(slots=True)
class Event:
    """A published event."""

    topic: str
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    source: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EventBus(ABC):
    """Publish/subscribe bus."""

    @abstractmethod
    def publish(self, event: Event) -> None: ...

    @abstractmethod
    def subscribe(self, topic: str, handler: EventHandler) -> None: ...


class InMemoryEventBus(EventBus):
    """Synchronous in-process pub/sub (default for local runs/tests)."""

    def __init__(self) -> None:
        self._subs: dict[str, list[EventHandler]] = {}

    def publish(self, event: Event) -> None:
        for handler in self._subs.get(event.topic, []):
            handler(event)

    def subscribe(self, topic: str, handler: EventHandler) -> None:
        self._subs.setdefault(topic, []).append(handler)
