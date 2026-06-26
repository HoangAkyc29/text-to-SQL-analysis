"""Item 11 - Output parser.

Turn raw model text into a structured object (JSON, pydantic model, regex
groups). Includes a retry/repair hook for malformed output.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class ParseResult(Generic[T]):
    """Outcome of parsing."""

    ok: bool
    value: T | None = None
    error: str | None = None
    raw: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class OutputParser(ABC, Generic[T]):
    """Parse raw text into ``T``."""

    @abstractmethod
    def parse(self, text: str) -> ParseResult[T]:
        """Parse ``text``; never raise, return a ParseResult instead."""

    def repair(self, text: str, error: str) -> str:
        """Optional best-effort repair of malformed text before re-parsing."""
        return text
