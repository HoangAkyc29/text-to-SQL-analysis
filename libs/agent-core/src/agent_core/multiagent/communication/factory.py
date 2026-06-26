"""Factory for communication transports and event buses."""

from __future__ import annotations

from commons.errors import ConfigError

from agent_core.infra.backends.config import A2AQueueBackendConfig, EventBusBackendConfig
from agent_core.infra.backends.resolve import resolve_url
from agent_core.multiagent.communication.base import InProcessTransport, MessageTransport
from agent_core.multiagent.event_bus.base import EventBus, InMemoryEventBus


def build_event_bus(config: EventBusBackendConfig) -> EventBus:
    backend = config.backend.lower()
    if backend == "in_memory":
        return InMemoryEventBus()
    if backend == "redis":
        url = resolve_url(config.url, config.url_env)
        if not url:
            raise ConfigError("redis event bus requires url or url_env", backend="redis")
        try:
            from agent_core.multiagent.event_bus.redis_bus import RedisEventBus
        except ImportError as exc:
            raise ConfigError(
                "redis event bus requires agent-core[redis]",
                backend="redis",
            ) from exc
        return RedisEventBus(url, channel_prefix=config.channel_prefix)
    raise ConfigError(f"Unknown event bus backend: {config.backend}", backend=config.backend)


def build_transport(config: A2AQueueBackendConfig) -> MessageTransport | None:
    backend = config.backend.lower()
    if backend in ("none", "in_process"):
        return InProcessTransport() if backend == "in_process" else None
    if backend == "redis":
        url = resolve_url(config.url, config.url_env)
        if not url:
            raise ConfigError("redis transport requires url or url_env", backend="redis")
        try:
            from agent_core.multiagent.communication.redis_transport import RedisMessageTransport
        except ImportError as exc:
            raise ConfigError(
                "redis transport requires agent-core[redis]",
                backend="redis",
            ) from exc
        return RedisMessageTransport(url, queue_prefix=config.queue_prefix)
    raise ConfigError(f"Unknown transport backend: {config.backend}", backend=config.backend)
