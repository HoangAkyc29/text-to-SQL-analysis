"""Item 46 - Notifications / Progress / Cancellation.

Out-of-band server messages: progress for long-running calls, cancellation, and
``*_list_changed`` notifications when the tool/resource/prompt set changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class Progress:
    """Progress report for a long-running operation."""

    token: str
    progress: float  # 0..1
    message: str = ""


class CancellationToken:
    """Cooperative cancellation flag."""

    def __init__(self) -> None:
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    @property
    def cancelled(self) -> bool:
        return self._cancelled


class Notifier(ABC):
    """Emit progress and list-changed notifications to clients."""

    @abstractmethod
    async def progress(self, report: Progress) -> None: ...

    @abstractmethod
    async def tools_list_changed(self) -> None: ...

    @abstractmethod
    async def resources_list_changed(self) -> None: ...

    @abstractmethod
    async def prompts_list_changed(self) -> None: ...
