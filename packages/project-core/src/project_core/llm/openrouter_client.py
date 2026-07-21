from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from project_core.config.loader import get_openrouter_api_key, load_models_config
from project_core.domain.errors.codes import LLMProviderError


@dataclass
class ChatCompletionResult:
    content: str
    raw: dict[str, Any]
    usage_tokens: int = 0


class _RetryableProviderError(LLMProviderError):
    pass


class OpenRouterClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 300.0,
        max_attempts: int = 3,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        self.api_key = api_key or get_openrouter_api_key()
        self.base_url = (base_url or "https://openrouter.ai/api/v1").rstrip("/")
        self.timeout = timeout
        self.max_attempts = max_attempts

    def profile_for_agent(self, agent_key: str) -> str:
        cfg = load_models_config()
        return cfg.agent_profiles.get(agent_key, cfg.default_profile)

    def _profile(self, profile_name: str) -> Any:
        cfg = load_models_config()
        if profile_name not in cfg.profiles:
            raise LLMProviderError(f"Unknown model profile: {profile_name}")
        return cfg.profiles[profile_name]

    def chat(
        self,
        *,
        profile_name: str,
        messages: list[dict[str, Any]],
        response_format: dict[str, Any] | None = None,
        timeout: float | None = None,
        max_attempts: int | None = None,
    ) -> ChatCompletionResult:
        request_timeout = self.timeout if timeout is None else timeout
        attempts = self.max_attempts if max_attempts is None else max_attempts
        if request_timeout <= 0:
            raise ValueError("timeout must be positive")
        if attempts <= 0:
            raise ValueError("max_attempts must be positive")
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

        retryer = Retrying(
            stop=stop_after_attempt(attempts),
            wait=wait_exponential(multiplier=0.5, max=8),
            retry=retry_if_exception_type(_RetryableProviderError),
            reraise=True,
        )
        data = retryer(self._request, payload, request_timeout)
        if not isinstance(data, dict):
            raise LLMProviderError("OpenRouter returned a non-object response")
        choice = (data.get("choices") or [{}])[0]
        if not isinstance(choice, dict):
            raise LLMProviderError("OpenRouter returned an invalid choice")
        message = choice.get("message") or {}
        if not isinstance(message, dict):
            raise LLMProviderError("OpenRouter returned an invalid message")
        content = message.get("content")
        if isinstance(content, list):
            parts: list[str] = []
            for block in content:
                if isinstance(block, dict):
                    text = block.get("text") or block.get("content")
                    if isinstance(text, str) and text.strip():
                        parts.append(text.strip())
                elif isinstance(block, str) and block.strip():
                    parts.append(block.strip())
            content = "\n".join(parts) if parts else ""
        elif content is None:
            content = ""
        else:
            content = str(content)
        if not content.strip():
            reasoning = message.get("reasoning")
            if isinstance(reasoning, str):
                content = reasoning
            elif isinstance(reasoning, dict):
                content = str(
                    reasoning.get("content") or reasoning.get("text") or reasoning.get("summary") or ""
                )
        if not str(content).strip():
            raise LLMProviderError("OpenRouter returned empty content")
        usage = data.get("usage") or {}
        tokens = int(usage.get("total_tokens") or 0)
        return ChatCompletionResult(content=content, raw=data, usage_tokens=tokens)

    def _request(self, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            raise _RetryableProviderError(
                f"OpenRouter request failed: {type(exc).__name__}"
            ) from exc
        if not response.ok:
            error = f"OpenRouter HTTP {response.status_code}: {response.text[:500]}"
            if response.status_code == 429 or response.status_code >= 500:
                raise _RetryableProviderError(error)
            raise LLMProviderError(error)
        try:
            data = response.json()
        except ValueError as exc:
            raise LLMProviderError("OpenRouter returned invalid JSON") from exc
        if not isinstance(data, dict):
            raise LLMProviderError("OpenRouter returned a non-object response")
        return data
