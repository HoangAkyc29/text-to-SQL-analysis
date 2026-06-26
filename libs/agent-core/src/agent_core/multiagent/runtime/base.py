"""Item 28 - Scheduler / Executor / Runtime.

The execution engine: *how* work runs (synchronously, async event loop, thread/
process pool, worker queue) and with what concurrency. Distinct from
orchestration (item 25, the topology) - the same supervisor graph can run on
different runtimes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

R = TypeVar("R")


@dataclass(slots=True)
class TaskHandle(Generic[R]):
    """A handle to a submitted unit of work."""

    id: str
    _result_getter: Callable[[], R]

    def result(self) -> R:
        return self._result_getter()


class Runtime(ABC):
    """Submit and run callables under a concurrency policy."""

    @abstractmethod
    def submit(self, fn: Callable[..., R], *args: Any, **kwargs: Any) -> TaskHandle[R]: ...

    @abstractmethod
    def map(self, fn: Callable[..., R], items: list[Any]) -> list[R]: ...

    def shutdown(self) -> None:  # pragma: no cover - optional
        """Release resources (pools, loops). Default no-op."""
        return None


class SyncRuntime(Runtime):
    """Trivial runtime that runs everything inline (default for local/tests)."""

    def submit(self, fn: Callable[..., R], *args: Any, **kwargs: Any) -> TaskHandle[R]:
        value = fn(*args, **kwargs)
        return TaskHandle(id="sync", _result_getter=lambda: value)

    def map(self, fn: Callable[..., R], items: list[Any]) -> list[R]:
        return [fn(item) for item in items]
