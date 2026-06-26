"""Resolve backend URLs from config + environment."""

from __future__ import annotations

import os


def resolve_url(url: str | None, url_env: str | None) -> str | None:
    if url_env and os.getenv(url_env):
        return os.getenv(url_env)
    return url
