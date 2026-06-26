"""Root exception hierarchy shared across the monorepo."""

from __future__ import annotations


class CommonsError(Exception):
    """Base class for all monorepo errors.

    Carries an optional machine-readable ``code`` and structured ``details``.
    """

    def __init__(self, message: str, *, code: str = "error", **details: object) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"[{self.code}] {self.message}"


class ConfigError(CommonsError):
    """Raised when configuration is missing or invalid."""

    def __init__(self, message: str, **details: object) -> None:
        super().__init__(message, code="config_error", **details)
