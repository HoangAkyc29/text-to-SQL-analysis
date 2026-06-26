"""Central registries built from platform.yaml."""

from platform_core.registry.agent_registry import PlatformAgentRegistry
from platform_core.registry.mcp_registry import PlatformMCPRegistry

__all__ = ["PlatformAgentRegistry", "PlatformMCPRegistry"]
