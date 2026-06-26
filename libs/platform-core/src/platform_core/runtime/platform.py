"""The ``AgentPlatform`` facade: load config and wire the control plane.

This is what an operator interacts with. It binds together the central agent
registry, the MCP registry, the router, and the graph orchestrator, all from one
``platform.yaml``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from commons.logging import get_logger

from platform_core.config.loader import load_platform_config
from platform_core.config.schema import PlatformConfig
from platform_core.orchestration.graph_orchestrator import GraphOrchestrator
from platform_core.registry.agent_registry import PlatformAgentRegistry
from platform_core.registry.mcp_registry import PlatformMCPRegistry
from platform_core.router.message_router import MessageRouter

log = get_logger("platform_core.platform")


class AgentPlatform:
    """Top-level control plane assembled from platform.yaml."""

    def __init__(self, config: PlatformConfig, *, transport: str = "in_process") -> None:
        self.config = config
        self.agents = PlatformAgentRegistry(config)
        self.mcp = PlatformMCPRegistry(config)
        self.router = MessageRouter(self.agents, transport=transport, config=config)
        self.orchestrator = GraphOrchestrator(config, self.router)

    @classmethod
    def from_config(
        cls, path: str | Path | None = None, *, transport: str = "in_process"
    ) -> "AgentPlatform":
        return cls(load_platform_config(path), transport=transport)

    def run_goal(
        self,
        goal: str,
        *,
        inputs: dict[str, Any] | None = None,
        actor_id: str = "platform",
    ) -> dict[str, Any]:
        """Run the whole agent graph for a goal."""
        return self.orchestrator.run(goal, inputs=inputs, actor_id=actor_id)
