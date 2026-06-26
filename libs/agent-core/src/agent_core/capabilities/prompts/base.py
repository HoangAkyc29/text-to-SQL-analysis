"""Item 7 - Prompt / Prompt template / management.

Render prompts from a context dict, manage few-shot examples, and version
prompts so a deployment can pin / roll back a specific revision.

    render(context) -> str
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PromptVersion:
    """A single immutable revision of a prompt."""

    version: str
    template: str
    few_shots: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class PromptTemplate(ABC):
    """Render a prompt for a given context."""

    def __init__(self, version: PromptVersion) -> None:
        self.version = version

    @abstractmethod
    def render(self, context: dict[str, Any]) -> str:
        """Return the fully rendered prompt string."""

    def with_few_shots(self) -> list[dict[str, str]]:
        return list(self.version.few_shots)


class StringPromptTemplate(PromptTemplate):
    """Default ``str.format``-based renderer."""

    def render(self, context: dict[str, Any]) -> str:
        try:
            return self.version.template.format(**context)
        except KeyError as exc:  # pragma: no cover - defensive
            raise KeyError(f"Missing prompt variable: {exc}") from exc


class PromptRepository(ABC):
    """Store/retrieve prompt versions (filesystem, DB, remote registry)."""

    @abstractmethod
    def get(self, name: str, version: str | None = None) -> PromptVersion:
        """Return a prompt version (latest if ``version`` is None)."""

    @abstractmethod
    def register(self, name: str, version: PromptVersion) -> None:
        """Persist a new prompt version."""
