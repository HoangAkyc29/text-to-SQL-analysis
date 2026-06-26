"""Redis-backed cache with TTL."""

from __future__ import annotations

import json
from typing import Any

from agent_core.infra.caching.base import Cache


class RedisCache(Cache):
    def __init__(self, url: str, *, key_prefix: str = "cache:", default_ttl: int = 3600) -> None:
        import redis

        self._client = redis.Redis.from_url(url, decode_responses=True)
        self._prefix = key_prefix
        self._default_ttl = default_ttl

    def get(self, key: str) -> Any | None:
        raw = self._client.get(f"{self._prefix}{key}")
        return json.loads(raw) if raw else None

    def set(self, key: str, value: Any, *, ttl_seconds: int | None = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        self._client.setex(f"{self._prefix}{key}", ttl, json.dumps(value, default=str))

    def delete(self, key: str) -> None:
        self._client.delete(f"{self._prefix}{key}")

    def clear(self) -> None:
        for key in self._client.scan_iter(f"{self._prefix}*"):
            self._client.delete(key)
