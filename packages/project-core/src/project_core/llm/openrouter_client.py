from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from project_core.config.loader import get_openrouter_api_key, load_models_config
from project_core.domain.errors.codes import LLMProviderError


@dataclass
class ChatCompletionResult:
    content: str
    raw: dict[str, Any]
    usage_tokens: int = 0


class OpenRouterClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.api_key = api_key or get_openrouter_api_key()
        self.base_url = (base_url or "https://openrouter.ai/api/v1").rstrip("/")
        self.timeout = timeout

    def profile_for_agent(self, agent_key: str) -> str:
        cfg = load_models_config()
        return cfg.agent_profiles.get(agent_key, cfg.default_profile)

    def _profile(self, profile_name: str) -> Any:
        cfg = load_models_config()
        if profile_name not in cfg.profiles:
            raise LLMProviderError(f"Unknown model profile: {profile_name}")
        return cfg.profiles[profile_name]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=8))
    def chat(
        self,
        *,
        profile_name: str,
        messages: list[dict[str, Any]],
        response_format: dict[str, Any] | None = None,
    ) -> ChatCompletionResult:
        profile = self._profile(profile_name)
        payload: dict[str, Any] = {
            "model": profile.model_id,
            "messages": messages,
            **profile.params,
        }
        if profile.reasoning:
            payload["reasoning"] = profile.reasoning
        if response_format:
            payload["response_format"] = response_format

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=self.timeout,
        )
        if not response.ok:
            raise LLMProviderError(
                f"OpenRouter HTTP {response.status_code}: {response.text[:500]}"
            )
        data = response.json()
        message = data["choices"][0]["message"]
        content = message.get("content") or ""
        usage = data.get("usage") or {}
        tokens = int(usage.get("total_tokens") or 0)
        return ChatCompletionResult(content=content, raw=data, usage_tokens=tokens)
