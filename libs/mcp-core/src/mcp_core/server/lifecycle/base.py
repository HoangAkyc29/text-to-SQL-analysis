"""Item 37 - MCP Server (base / lifecycle).

The server lifecycle: initialize -> negotiate -> serve -> shutdown, plus
registration of the tool/resource/prompt handlers. ``initialize`` performs
version negotiation (protocolVersion) and capability discovery.

A FastMCP-backed reference implementation is provided so concrete servers only
register their providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from commons.logging import get_logger

if TYPE_CHECKING:
    from mcp_core.server.capabilities.base import CapabilitySet
    from mcp_core.server.providers.prompts.base import PromptProvider
    from mcp_core.server.providers.resources.base import ResourceProvider
    from mcp_core.server.providers.tools.base import ToolProvider
    from mcp_core.server.transport.base import ServerTransport

log = get_logger(__name__)


@dataclass(slots=True)
class ServerInfo:
    """Identity advertised during the MCP handshake."""

    name: str
    version: str = "0.1.0"
    protocol_version: str = "2025-06-18"
    instructions: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class AbstractMCPServer(ABC):
    """Base MCP server defining the lifecycle and provider registration."""

    def __init__(
        self,
        info: ServerInfo,
        *,
        transport: "ServerTransport | None" = None,
        capabilities: "CapabilitySet | None" = None,
    ) -> None:
        self.info = info
        self.transport = transport
        self.capabilities = capabilities
        self._tool_providers: list["ToolProvider"] = []
        self._resource_providers: list["ResourceProvider"] = []
        self._prompt_providers: list["PromptProvider"] = []

    # --- registration -----------------------------------------------------
    def add_tool_provider(self, provider: "ToolProvider") -> None:
        self._tool_providers.append(provider)

    def add_resource_provider(self, provider: "ResourceProvider") -> None:
        self._resource_providers.append(provider)

    def add_prompt_provider(self, provider: "PromptProvider") -> None:
        self._prompt_providers.append(provider)

    # --- lifecycle --------------------------------------------------------
    @abstractmethod
    def initialize(self) -> None:
        """Negotiate protocol version + capabilities and bind handlers."""

    @abstractmethod
    def serve(self) -> None:
        """Run the server (blocking) over the configured transport."""

    @abstractmethod
    def shutdown(self) -> None:
        """Release resources and stop serving."""

    def run(self) -> None:
        """Convenience driver: initialize then serve, ensuring shutdown."""
        self.initialize()
        try:
            self.serve()
        finally:
            self.shutdown()
