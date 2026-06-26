"""Item 26 - Agent registry / Discovery / Factory.

Create, register and find agents by capability.

    register(card)            -> add an agent
    discover(capability)      -> find agents that can do X
    create(name)              -> instantiate an agent (factory)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentCard:
    """Public description of an agent (name, capabilities, endpoint)."""

    name: str
    description: str = ""
    capabilities: list[str] = field(default_factory=list)
    endpoint: str | None = None  # for network-addressable agents
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentFactory(ABC):
    """Instantiate an agent by name/config."""

    @abstractmethod
    def create(self, name: str, *, config: dict[str, Any] | None = None) -> Any: ...


class AgentRegistry(ABC):
    """Hold agent cards and resolve agents by capability."""

    def __init__(self) -> None:
        self._cards: dict[str, AgentCard] = {}

    def register(self, card: AgentCard) -> None:
        self._cards[card.name] = card

    def get(self, name: str) -> AgentCard:
        return self._cards[name]

    def all(self) -> list[AgentCard]:
        return list(self._cards.values())

    def discover(self, capability: str) -> list[AgentCard]:
        return [c for c in self._cards.values() if capability in c.capabilities]
