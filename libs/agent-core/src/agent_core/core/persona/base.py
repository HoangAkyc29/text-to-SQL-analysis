"""Item 2 - Role / Persona / config.

A Persona captures the agent's identity, tone, goals and constraints, and knows
how to serialise itself into a system-prompt fragment.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class PersonaConfig(BaseModel):
    """Declarative persona definition (load from YAML/JSON/env)."""

    name: str
    role: str = "assistant"
    goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    tone: str = "concise, professional"
    language: str = "en"


class Persona(ABC):
    """Renders a persona into a prompt fragment."""

    def __init__(self, config: PersonaConfig) -> None:
        self.config = config

    @abstractmethod
    def to_system_prompt(self) -> str:
        """Return the persona as a system-prompt fragment."""


class TemplatePersona(Persona):
    """Default persona renderer using a simple text template."""

    def to_system_prompt(self) -> str:
        c = self.config
        lines = [f"You are {c.name}, acting as a {c.role}.", f"Tone: {c.tone}. Language: {c.language}."]
        if c.goals:
            lines.append("Goals:\n" + "\n".join(f"- {g}" for g in c.goals))
        if c.constraints:
            lines.append("Constraints:\n" + "\n".join(f"- {x}" for x in c.constraints))
        return "\n".join(lines)
