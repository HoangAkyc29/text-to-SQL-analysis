"""Base settings for env-driven configuration.

Every agent / server defines its own settings subclass. Reading from the
environment (and a local ``.env``) is centralised here so behaviour is uniform.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseAppSettings(BaseSettings):
    """Common settings shared by all services."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    log_level: str = "INFO"
