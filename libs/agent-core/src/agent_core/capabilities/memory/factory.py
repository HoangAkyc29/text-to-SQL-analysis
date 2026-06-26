"""Factory for short-term and long-term memory backends."""

from __future__ import annotations

from pathlib import Path

from commons.errors import ConfigError

from agent_core.capabilities.memory.base import LongTermMemory, ShortTermMemory
from agent_core.capabilities.memory.sqlite_ltm import SQLiteLongTermMemory
from agent_core.capabilities.memory.strands_stm import InMemoryShortTermMemory
from agent_core.infra.backends.config import LTMBackendConfig, STMBackendConfig
from agent_core.infra.backends.resolve import resolve_url


def build_stm(config: STMBackendConfig, *, base_dir: Path | None = None) -> ShortTermMemory:
    backend = config.backend.lower()
    if backend == "in_memory":
        return InMemoryShortTermMemory()
    if backend == "file":
        from agent_core.capabilities.memory.strands_stm import StrandsSTM

        root = Path(config.dir)
        if base_dir and not root.is_absolute():
            root = base_dir / root
        return _FileSTMWrapper(StrandsSTM(root))
    if backend == "redis":
        url = resolve_url(config.url, config.url_env)
        if not url:
            raise ConfigError("redis STM requires url or url_env", backend="redis")
        try:
            from agent_core.capabilities.memory.redis_stm import RedisShortTermMemory
        except ImportError as exc:
            raise ConfigError(
                "redis STM requires agent-core[redis]: pip install 'agent-core[redis]'",
                backend="redis",
            ) from exc
        return RedisShortTermMemory(url, key_prefix=config.key_prefix)
    raise ConfigError(f"Unknown STM backend: {config.backend}", backend=config.backend)


def build_ltm(config: LTMBackendConfig, *, base_dir: Path | None = None) -> LongTermMemory:
    backend = config.backend.lower()
    if backend == "sqlite":
        db_path = Path(config.db_path)
        if base_dir and not db_path.is_absolute():
            db_path = base_dir / db_path
        return SQLiteLongTermMemory(db_path)
    if backend == "mongodb":
        url = resolve_url(config.url, config.url_env)
        if not url:
            raise ConfigError("mongodb LTM requires url or url_env", backend="mongodb")
        try:
            from agent_core.capabilities.memory.mongodb_ltm import MongoLongTermMemory
        except ImportError as exc:
            raise ConfigError(
                "mongodb LTM requires agent-core[mongodb]",
                backend="mongodb",
            ) from exc
        return MongoLongTermMemory(url, database=config.database, collection=config.collection)
    if backend == "redis":
        url = resolve_url(config.url, config.url_env)
        if not url:
            raise ConfigError("redis LTM requires url or url_env", backend="redis")
        try:
            from agent_core.capabilities.memory.redis_ltm import RedisLongTermMemory
        except ImportError as exc:
            raise ConfigError(
                "redis LTM requires agent-core[redis]",
                backend="redis",
            ) from exc
        return RedisLongTermMemory(url, key_prefix="ltm:")
    raise ConfigError(f"Unknown LTM backend: {config.backend}", backend=config.backend)


class _FileSTMWrapper(ShortTermMemory):
    """Adapt StrandsSTM file sessions to ShortTermMemory transcript API."""

    def __init__(self, strands_stm: object) -> None:
        self._inner = strands_stm
        self._transcript: dict[str, list[dict[str, str]]] = {}

    def append(self, session_id: str, role: str, content: str) -> None:
        self._transcript.setdefault(session_id, []).append({"role": role, "content": content})

    def history(self, session_id: str, *, limit: int | None = None) -> list[dict[str, str]]:
        turns = self._transcript.get(session_id, [])
        return turns[-limit:] if limit else list(turns)

    def reset(self, session_id: str) -> None:
        self._transcript.pop(session_id, None)

    def create_session_manager(self, session_id: str) -> object:
        return self._inner.create_session_manager(session_id)  # type: ignore[attr-defined]
