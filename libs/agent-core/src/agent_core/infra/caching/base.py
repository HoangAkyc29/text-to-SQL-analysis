"""Item 34 - Caching.

Cache LLM responses and tool results to cut latency and cost. Keyed by a stable
hash of the request.
"""

from __future__ import annotations

import hashlib
import json
import time
from abc import ABC, abstractmethod
from typing import Any


def cache_key(*parts: Any) -> str:
    """Build a stable cache key from arbitrary JSON-serialisable parts."""
    blob = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class Cache(ABC):
    """Key-value cache with optional TTL."""

    @abstractmethod
    def get(self, key: str) -> Any | None: ...

    @abstractmethod
    def set(self, key: str, value: Any, *, ttl_seconds: int | None = None) -> None: ...

    def delete(self, key: str) -> None:
        """Remove a key. Override in concrete caches."""

    def clear(self) -> None:
        """Remove all keys. Override in concrete caches."""


class InMemoryCache(Cache):
    """Dict-backed cache with optional per-entry TTL."""

    def __init__(self, *, default_ttl: int | None = None) -> None:
        self._store: dict[str, Any] = {}
        self._expires: dict[str, float] = {}
        self.default_ttl = default_ttl

    def _expired(self, key: str) -> bool:
        exp = self._expires.get(key)
        return exp is not None and time.monotonic() > exp

    def get(self, key: str) -> Any | None:
        if self._expired(key):
            self.delete(key)
            return None
        return self._store.get(key)

    def set(self, key: str, value: Any, *, ttl_seconds: int | None = None) -> None:
        self._store[key] = value
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        if ttl:
            self._expires[key] = time.monotonic() + ttl
        else:
            self._expires.pop(key, None)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)
        self._expires.pop(key, None)

    def clear(self) -> None:
        self._store.clear()
        self._expires.clear()
