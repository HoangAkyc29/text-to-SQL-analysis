"""Redis pub/sub event bus."""

from __future__ import annotations

import json
import threading
from collections.abc import Callable

from agent_core.multiagent.event_bus.base import Event, EventBus, EventHandler


class RedisEventBus(EventBus):
    def __init__(self, url: str, *, channel_prefix: str = "events:") -> None:
        import redis

        self._client = redis.Redis.from_url(url, decode_responses=True)
        self._pub = redis.Redis.from_url(url, decode_responses=True)
        self._prefix = channel_prefix
        self._subs: dict[str, list[EventHandler]] = {}
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def _channel(self, topic: str) -> str:
        return f"{self._prefix}{topic}"

    def publish(self, event: Event) -> None:
        payload = json.dumps(
            {
                "topic": event.topic,
                "payload": event.payload,
                "id": event.id,
                "source": event.source,
                "created_at": event.created_at.isoformat(),
            },
            default=str,
        )
        self._pub.publish(self._channel(event.topic), payload)
        for handler in self._subs.get(event.topic, []):
            handler(event)

    def subscribe(self, topic: str, handler: EventHandler) -> None:
        self._subs.setdefault(topic, []).append(handler)
