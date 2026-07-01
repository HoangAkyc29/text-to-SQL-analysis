"""Opt-in live LLM tests."""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.live


@pytest.mark.skipif(
    os.getenv("ALLOW_LLM_STUB", "1") == "1" or not os.getenv("OPENROUTER_API_KEY"),
    reason="Set ALLOW_LLM_STUB=0 and OPENROUTER_API_KEY for live LLM test",
)
def test_live_openrouter_ping():
    from project_core.llm.openrouter_client import OpenRouterClient

    client = OpenRouterClient()
    result = client.chat(
        profile_name="router",
        messages=[{"role": "user", "content": "Reply with JSON: {\"ok\": true}"}],
        response_format={"type": "json_object"},
    )
    assert result.content
