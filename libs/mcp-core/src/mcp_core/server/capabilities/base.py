"""Item 39 - Capability negotiation.

Declares which primitives (tools/resources/prompts) and features (e.g.
list_changed notifications, subscribe) the server supports. Sent during the
initialize handshake so the client knows what it can use.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CapabilitySet:
    """Server capabilities advertised at handshake."""

    tools: bool = False
    resources: bool = False
    prompts: bool = False
    # feature flags
    tools_list_changed: bool = False
    resources_subscribe: bool = False
    resources_list_changed: bool = False
    prompts_list_changed: bool = False
    logging: bool = False

    def to_dict(self) -> dict[str, dict[str, bool]]:
        """Serialise into the MCP capabilities shape."""
        caps: dict[str, dict[str, bool]] = {}
        if self.tools:
            caps["tools"] = {"listChanged": self.tools_list_changed}
        if self.resources:
            caps["resources"] = {
                "subscribe": self.resources_subscribe,
                "listChanged": self.resources_list_changed,
            }
        if self.prompts:
            caps["prompts"] = {"listChanged": self.prompts_list_changed}
        if self.logging:
            caps["logging"] = {}
        return caps
