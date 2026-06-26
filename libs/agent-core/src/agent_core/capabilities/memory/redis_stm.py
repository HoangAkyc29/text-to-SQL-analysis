"""Redis-backed short-term memory."""

from __future__ import annotations

import json

from agent_core.capabilities.memory.base import ShortTermMemory


class RedisShortTermMemory(ShortTermMemory):
    def __init__(self, url: str, *, key_prefix: str = "stm:") -> None:
        import redis

        self._client = redis.Redis.from_url(url, decode_responses=True)
        self._prefix = key_prefix

    def _key(self, session_id: str) -> str:
        return f"{self._prefix}{session_id}"

    def append(self, session_id: str, role: str, content: str) -> None:
        self._client.rpush(self._key(session_id), json.dumps({"role": role, "content": content}))

    def history(self, session_id: str, *, limit: int | None = None) -> list[dict[str, str]]:
        key = self._key(session_id)
        if limit:
            raw = self._client.lrange(key, -limit, -1)
        else:
            raw = self._client.lrange(key, 0, -1)
        return [json.loads(x) for x in raw]

    def reset(self, session_id: str) -> None:
        self._client.delete(self._key(session_id))
