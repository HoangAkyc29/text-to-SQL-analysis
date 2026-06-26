"""Thread-pool runtime for parallel graph node execution."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar
from uuid import uuid4

from agent_core.multiagent.runtime.base import Runtime, TaskHandle

R = TypeVar("R")


class ThreadPoolRuntime(Runtime):
    """Execute callables in a bounded thread pool."""

    def __init__(self, max_workers: int = 4) -> None:
        self._max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, fn: Callable[..., R], *args: Any, **kwargs: Any) -> TaskHandle[R]:
        future = self._executor.submit(fn, *args, **kwargs)
        return TaskHandle(id=uuid4().hex[:8], _result_getter=future.result)

    def map(self, fn: Callable[..., R], items: list[Any]) -> list[R]:
        if not items:
            return []
        futures = [self._executor.submit(fn, item) for item in items]
        return [f.result() for f in futures]

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)
