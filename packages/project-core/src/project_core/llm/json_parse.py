"""Parse JSON from LLM chat completions."""

from __future__ import annotations

import json
import re
from typing import Any

from project_core.domain.errors.codes import LLMProviderError
from project_core.llm.openrouter_client import ChatCompletionResult


def completion_text(result: ChatCompletionResult) -> str:
    """Return the best-effort assistant text from an OpenRouter completion."""
    message = (result.raw.get("choices") or [{}])[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                text = block.get("text") or block.get("content")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
            elif isinstance(block, str) and block.strip():
                parts.append(block.strip())
        if parts:
            return "\n".join(parts)
    reasoning = message.get("reasoning")
    if isinstance(reasoning, str) and reasoning.strip():
        return reasoning.strip()
    if isinstance(reasoning, dict):
        for key in ("content", "text", "summary"):
            val = reasoning.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
    refusal = message.get("refusal")
    if isinstance(refusal, str) and refusal.strip():
        return refusal.strip()
    return ""


def extract_llm_json(text: str) -> dict[str, Any]:
    """Parse a JSON object from raw LLM output (handles fenced blocks)."""
    raw = (text or "").strip()
    if not raw:
        raise LLMProviderError("LLM returned empty content")
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start < 0 or end <= start:
            # Some models emit Python-literal dicts with single quotes.
            data = _try_literal_dict(raw)
            if data is None:
                raise LLMProviderError(f"LLM returned non-JSON content: {raw[:300]}") from None
        else:
            snippet = raw[start : end + 1]
            try:
                data = json.loads(snippet)
            except json.JSONDecodeError as exc:
                data = _try_literal_dict(snippet) or _try_literal_dict(raw)
                if data is None:
                    raise LLMProviderError(f"LLM returned invalid JSON: {raw[:300]}") from exc
    if not isinstance(data, dict):
        raise LLMProviderError("LLM JSON payload must be an object")
    return data


def _try_literal_dict(raw: str) -> dict[str, Any] | None:
    """Best-effort parse of single-quoted / Python-literal object payloads."""
    import ast

    text = (raw or "").strip()
    if not text or text[0] not in "{[":
        return None
    try:
        value = ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def parse_llm_json(result: ChatCompletionResult) -> dict[str, Any]:
    return extract_llm_json(completion_text(result))
