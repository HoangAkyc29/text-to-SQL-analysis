"""Item 41 - Resource provider (primitive: read-only data).

Resources are application-controlled, URI-addressed read-only data. They map to
the agent side's Memory / Retriever sources (items 12/13).

    list_resources()        -> [ResourceDefinition]
    read_resource(uri)      -> content
    subscribe(uri)          -> notify on change (optional)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ResourceDefinition:
    """Declarative resource description + reader."""

    uri: str
    name: str
    reader: Callable[[], Any]
    description: str = ""
    mime_type: str = "application/json"
    metadata: dict[str, Any] = field(default_factory=dict)


class ResourceProvider(ABC):
    """Provide read-only resources and bind them to a server."""

    @abstractmethod
    def list_resources(self) -> list[ResourceDefinition]:
        """Return the resources this provider exposes."""

    def read_resource(self, uri: str) -> Any:
        for res in self.list_resources():
            if res.uri == uri:
                return res.reader()
        raise KeyError(f"Unknown resource: {uri}")

    def subscribe(self, uri: str, callback: Callable[[str, Any], None]) -> None:
        """Optional change subscription. Default: unsupported (no-op)."""
        return None

    def bind(self, mcp: Any) -> None:
        """Register every resource on a FastMCP instance."""
        for res in self.list_resources():
            mcp.resource(res.uri, name=res.name, description=res.description)(res.reader)
