"""Factory for cache backends."""

from __future__ import annotations

from commons.errors import ConfigError

from agent_core.infra.backends.config import CacheBackendConfig
from agent_core.infra.backends.resolve import resolve_url
from agent_core.infra.caching.base import Cache, InMemoryCache


def build_cache(config: CacheBackendConfig) -> Cache:
    backend = config.backend.lower()
    if backend == "in_memory":
        return InMemoryCache(default_ttl=config.ttl_seconds)
    if backend == "redis":
        url = resolve_url(config.url, config.url_env)
        if not url:
            raise ConfigError("redis cache requires url or url_env", backend="redis")
        try:
            from agent_core.infra.caching.redis_cache import RedisCache
        except ImportError as exc:
            raise ConfigError(
                "redis cache requires agent-core[redis]",
                backend="redis",
            ) from exc
        try:
            return RedisCache(url, key_prefix=config.key_prefix, default_ttl=config.ttl_seconds)
        except ImportError as exc:
            raise ConfigError(
                "redis cache requires agent-core[redis]: pip install 'agent-core[redis]'",
                backend="redis",
            ) from exc
    raise ConfigError(f"Unknown cache backend: {config.backend}", backend=config.backend)
