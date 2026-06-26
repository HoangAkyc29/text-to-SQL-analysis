"""Load and normalise ``platform.yaml``."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from commons.errors import ConfigError

from platform_core.config.schema import (
    AgentSpec,
    MCPServerSpec,
    PlatformConfig,
)


def _default_config_path() -> Path:
    """Find platform.yaml: env override, CWD, or repo root above this file."""
    env = os.getenv("PLATFORM_CONFIG")
    if env:
        return Path(env)
    cwd = Path.cwd() / "platform.yaml"
    if cwd.exists():
        return cwd
    # Walk up from this file looking for a platform.yaml (repo root).
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "platform.yaml"
        if candidate.exists():
            return candidate
    return cwd


def load_platform_config(path: str | Path | None = None) -> PlatformConfig:
    """Parse platform.yaml into a :class:`PlatformConfig`."""
    cfg_path = Path(path) if path else _default_config_path()
    if not cfg_path.exists():
        raise ConfigError(f"platform.yaml not found at {cfg_path}")
    raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}

    # Inject the dict keys as names so each spec is self-describing.
    raw_servers = raw.get("mcp_servers", {}) or {}
    raw["mcp_servers"] = {
        name: MCPServerSpec(name=name, **spec) for name, spec in raw_servers.items()
    }
    raw_agents = raw.get("agents", {}) or {}
    raw["agents"] = {name: AgentSpec(name=name, **spec) for name, spec in raw_agents.items()}

    config = PlatformConfig(**raw)
    config.base_dir = cfg_path.parent
    return config
