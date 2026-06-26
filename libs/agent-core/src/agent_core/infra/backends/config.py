"""Backend configuration models for memory, cache, and communication."""

from __future__ import annotations

from pydantic import BaseModel, Field


class STMBackendConfig(BaseModel):
    backend: str = "in_memory"  # in_memory | file | redis
    dir: str = "./data/stm"
    url_env: str | None = None
    url: str | None = None
    key_prefix: str = "stm:"


class LTMBackendConfig(BaseModel):
    backend: str = "sqlite"  # sqlite | mongodb | redis
    db_path: str = "./data/ltm.db"
    collection: str = "memories"
    url_env: str | None = None
    url: str | None = None
    database: str = "agent_platform"


class RetrievalBackendConfig(BaseModel):
    backend: str = "none"  # none | in_memory_vector | chroma
    embedding: str = "openai"  # openai | local
    top_k: int = 5
    persist_dir: str = "./data/vectors"


class CacheBackendConfig(BaseModel):
    backend: str = "in_memory"  # in_memory | redis
    ttl_seconds: int = 3600
    url_env: str | None = None
    url: str | None = None
    key_prefix: str = "cache:"


class EventBusBackendConfig(BaseModel):
    backend: str = "in_memory"  # in_memory | redis
    url_env: str | None = None
    url: str | None = None
    channel_prefix: str = "events:"


class A2AQueueBackendConfig(BaseModel):
    backend: str = "none"  # none | redis
    url_env: str | None = None
    url: str | None = None
    queue_prefix: str = "a2a:"


class CommunicationConfig(BaseModel):
    event_bus: EventBusBackendConfig = Field(default_factory=EventBusBackendConfig)
    a2a_queue: A2AQueueBackendConfig = Field(default_factory=A2AQueueBackendConfig)
