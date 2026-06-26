"""HTTPS client configuration for A2A routing."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class A2AClientConfig:
    verify_ssl: bool = True
    ca_bundle: str | None = None
    client_cert: tuple[str, str] | None = None
    bearer_token: str | None = None
    timeout: float = 300.0
