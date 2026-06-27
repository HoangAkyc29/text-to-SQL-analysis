from __future__ import annotations

import os
from pathlib import Path

from project_core.config.loader import load_models_config
from project_core.llm.openrouter_client import OpenRouterClient


def get_llm_client(profile_name: str | None = None) -> OpenRouterClient:
    return OpenRouterClient()


def agent_profile(agent_key: str) -> str:
    models = load_models_config()
    return models.agent_profiles.get(agent_key, models.default_profile)
