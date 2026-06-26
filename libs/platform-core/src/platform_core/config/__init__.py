"""Platform configuration: schema + loader for platform.yaml."""

from platform_core.config.loader import load_platform_config
from platform_core.config.schema import (
    AgentSpec,
    MCPServerSpec,
    MemoryConfig,
    OrchestrationConfig,
    PlatformConfig,
)

__all__ = [
    "AgentSpec",
    "MCPServerSpec",
    "MemoryConfig",
    "OrchestrationConfig",
    "PlatformConfig",
    "load_platform_config",
]
