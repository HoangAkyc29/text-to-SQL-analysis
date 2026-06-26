"""Common type aliases and a lightweight Result wrapper."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeAlias, TypeVar

T = TypeVar("T")
E = TypeVar("E")

# A JSON-compatible value. Kept loose on purpose for transport payloads.
JSONValue: TypeAlias = "str | int | float | bool | None | list[JSONValue] | dict[str, JSONValue]"


@dataclass(slots=True)
class Result(Generic[T, E]):
    """Minimal success/error container to avoid exceptions on hot paths.

    Use :meth:`ok` / :meth:`err` to construct, and check :attr:`success`.
    """

    success: bool
    value: T | None = None
    error: E | None = None
    meta: dict[str, JSONValue] = field(default_factory=dict)

    @classmethod
    def ok(cls, value: T, **meta: JSONValue) -> "Result[T, E]":
        return cls(success=True, value=value, meta=dict(meta))

    @classmethod
    def err(cls, error: E, **meta: JSONValue) -> "Result[T, E]":
        return cls(success=False, error=error, meta=dict(meta))

    def unwrap(self) -> T:
        if not self.success:
            raise ValueError(f"Result is an error: {self.error!r}")
        return self.value  # type: ignore[return-value]
