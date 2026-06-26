"""Item 26 concrete - the central agent registry / factory.

Populated entirely from ``platform.yaml``. Resolves agents by name or
capability, exposes their endpoint (for HTTP A2A), and lazily instantiates an
agent's service via its ``factory`` dotted-path (for in-process A2A).
"""

from __future__ import annotations

import importlib
import os
from typing import Any

from commons.errors import ConfigError
from commons.logging import get_logger

from agent_core.multiagent.registry.base import AgentCard, AgentFactory, AgentRegistry

from platform_core.config.schema import AgentSpec, PlatformConfig

log = get_logger("platform_core.agent_registry")


class PlatformAgentRegistry(AgentRegistry, AgentFactory):
    """Central registry + factory backed by the platform config."""

    def __init__(self, config: PlatformConfig) -> None:
        super().__init__()
        self._config = config
        self._services: dict[str, Any] = {}
        for name, spec in config.agents.items():
            self.register(
                AgentCard(
                    name=name,
                    capabilities=spec.capabilities,
                    endpoint=self._resolve_endpoint(spec),
                    metadata={"skill": spec.skill or "", "mcp_servers": spec.mcp_servers},
                )
            )

    @staticmethod
    def _resolve_endpoint(spec: AgentSpec) -> str | None:
        if spec.endpoint_env and os.getenv(spec.endpoint_env):
            return os.getenv(spec.endpoint_env)
        return spec.endpoint

    def spec(self, name: str) -> AgentSpec:
        if name not in self._config.agents:
            raise ConfigError(f"Unknown agent: {name}")
        return self._config.agents[name]

    def resolve_capability(self, capability: str) -> str:
        """Return the agent name that provides ``capability``."""
        cards = self.discover(capability)
        if not cards:
            raise ConfigError(f"No agent provides capability '{capability}'")
        return cards[0].name

    # --- AgentFactory: in-process instantiation --------------------------
    def create(self, name: str, *, config: dict[str, Any] | None = None) -> Any:
        """Import and build the agent service from its factory dotted-path.

        Cached so repeated graph runs reuse the same service (and its memory).
        """
        if name in self._services:
            return self._services[name]
        spec = self.spec(name)
        module_path, _, attr = spec.factory.partition(":")
        if not attr:
            raise ConfigError(f"agent '{name}' factory must be 'module:callable', got {spec.factory!r}")
        log.info("Instantiating agent '%s' from %s", name, spec.factory)
        module = importlib.import_module(module_path)
        factory = getattr(module, attr)
        service = factory(self._config, spec)
        self._services[name] = service
        return service
