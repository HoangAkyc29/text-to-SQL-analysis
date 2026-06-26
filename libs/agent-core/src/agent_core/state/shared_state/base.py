"""Item 15 - Shared / Global State (blackboard).

A shared workspace multiple agents read/write to coordinate indirectly. Supports
namespaced keys and optional change notifications so a coordinator can react.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class Blackboard(ABC):
    """Concurrent shared key-value store for multi-agent coordination."""

    @abstractmethod
    def read(self, key: str, default: Any = None) -> Any: ...

    @abstractmethod
    def write(self, key: str, value: Any, *, author: str = "") -> None: ...

    @abstractmethod
    def keys(self, *, prefix: str = "") -> list[str]: ...

    def watch(self, key: str, callback: Callable[[str, Any], None]) -> None:
        """Subscribe to changes of ``key``. Default is a no-op for stores that
        do not support notifications."""
        return None
