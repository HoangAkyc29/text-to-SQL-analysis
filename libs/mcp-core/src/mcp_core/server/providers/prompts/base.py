"""Item 42 - Prompt provider (primitive: template).

Prompts are user-controlled, reusable templates surfaced to the user/client.
They map to the agent side's PromptTemplate (item 7).

    list_prompts()          -> [PromptDefinition]
    get_prompt(name, args)  -> rendered messages
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PromptDefinition:
    """Declarative prompt template description + renderer."""

    name: str
    renderer: Callable[..., str]
    description: str = ""
    arguments: list[dict[str, Any]] = field(default_factory=list)


class PromptProvider(ABC):
    """Provide reusable prompts and bind them to a server."""

    @abstractmethod
    def list_prompts(self) -> list[PromptDefinition]:
        """Return the prompts this provider exposes."""

    def get_prompt(self, name: str, arguments: dict[str, Any]) -> str:
        for prompt in self.list_prompts():
            if prompt.name == name:
                return prompt.renderer(**arguments)
        raise KeyError(f"Unknown prompt: {name}")

    def bind(self, mcp: Any) -> None:
        """Register every prompt on a FastMCP instance."""
        for prompt in self.list_prompts():
            mcp.prompt(name=prompt.name, description=prompt.description)(prompt.renderer)
