"""Wire platform backends from :class:`PlatformConfig`."""

from __future__ import annotations

from pathlib import Path

from agent_core.capabilities.memory.factory import build_ltm, build_stm
from agent_core.capabilities.retrieval.factory import build_retriever
from agent_core.infra.caching.factory import build_cache
from agent_core.multiagent.communication.factory import build_event_bus, build_transport

from platform_core.config.schema import PlatformConfig


def build_platform_backends(config: PlatformConfig) -> dict:
    """Instantiate memory, cache, communication backends from config."""
    base = config.base_dir
    mem = config.memory
    return {
        "stm": build_stm(mem.resolved_stm(), base_dir=base),
        "ltm": build_ltm(mem.resolved_ltm(), base_dir=base),
        "retriever": build_retriever(mem.retrieval, base_dir=base),
        "cache": build_cache(config.cache),
        "event_bus": build_event_bus(config.communication.event_bus),
        "transport": build_transport(config.communication.a2a_queue),
    }
