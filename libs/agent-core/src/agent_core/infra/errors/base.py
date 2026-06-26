"""Item 30 - Error / Retry policy.

Declarative retry/backoff policy plus a helper to apply it. Concrete agents
classify which exceptions are transient by overriding ``is_transient``.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class RetryConfig:
    max_retries: int = 2
    base_delay: float = 1.0
    backoff: float = 2.0
    max_delay: float = 30.0


class RetryPolicy(ABC):
    """Decide whether/when to retry."""

    def __init__(self, config: RetryConfig | None = None) -> None:
        self.config = config or RetryConfig()

    @abstractmethod
    def is_transient(self, exc: BaseException) -> bool:
        """Return True if ``exc`` is worth retrying."""

    def delay_for(self, attempt: int) -> float:
        d = self.config.base_delay * (self.config.backoff**attempt)
        return min(d, self.config.max_delay)


def with_retry(fn: Callable[[], T], policy: RetryPolicy, *, sleep: Callable[[float], None] = time.sleep) -> T:
    """Execute ``fn`` applying ``policy`` on transient failures."""
    attempt = 0
    while True:
        try:
            return fn()
        except BaseException as exc:  # noqa: BLE001 - policy decides
            if attempt >= policy.config.max_retries or not policy.is_transient(exc):
                raise
            sleep(policy.delay_for(attempt))
            attempt += 1
