from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from project_core.domain.analysis.chart_reviewer import ChartReviewer
from project_core.llm.openrouter_client import ChatCompletionResult


def _chart(path: Path) -> None:
    image = Image.new("RGB", (240, 160), "white")
    ImageDraw.Draw(image).rectangle((40, 30, 180, 130), fill="navy")
    image.save(path)


class FakeVisionClient:
    def __init__(self, payload: dict[str, Any] | None = None, error: Exception | None = None):
        self.payload = payload or {
            "verdict": "pass",
            "severity": "info",
            "issues": [],
            "fix_args": None,
        }
        self.error = error
        self.calls: list[dict[str, Any]] = []

    def chat(self, **kwargs: Any) -> ChatCompletionResult:
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return ChatCompletionResult(content=json.dumps(self.payload), raw={})


def test_vision_review_uses_multimodal_structured_message(tmp_path: Path) -> None:
    chart = tmp_path / "chart.png"
    _chart(chart)
    llm = FakeVisionClient()

    result = ChartReviewer(llm=llm, profile_name="openrouter_vision").review(
        chart,
        allowed_root=tmp_path,
        source_data=[{"label": "a", "value": 1}],
        chart_context={"intent": "compare values", "ignored": "not forwarded"},
    )

    assert result.verdict == "pass"
    assert result.reviewer == "vision"
    assert result.vision_available is True
    assert result.review_attempts == 1
    call = llm.calls[0]
    assert call["response_format"]["type"] == "json_schema"
    content = call["messages"][1]["content"]
    assert content[0]["type"] == "text"
    assert content[1]["type"] == "image_url"
    assert content[1]["image_url"]["url"].startswith("data:image/png;base64,")


def test_unsupported_vision_profile_returns_unavailable(tmp_path: Path) -> None:
    chart = tmp_path / "chart.png"
    _chart(chart)
    llm = FakeVisionClient()

    result = ChartReviewer(llm=llm, profile_name="openrouter_fast").review(
        chart,
        allowed_root=tmp_path,
    )

    assert result.verdict == "unavailable"
    assert result.vision_available is False
    assert "vision_profile_not_supported" in result.issues
    assert not llm.calls


def test_provider_or_contract_failure_returns_unavailable(tmp_path: Path) -> None:
    chart = tmp_path / "chart.png"
    _chart(chart)
    llm = FakeVisionClient(error=TimeoutError("provider timed out"))

    result = ChartReviewer(llm=llm, profile_name="openrouter_vision").review(
        chart,
        allowed_root=tmp_path,
    )

    assert result.verdict == "unavailable"
    assert result.issues == ["vision_review_unavailable"]


def test_deterministic_failure_skips_vision(tmp_path: Path) -> None:
    chart = tmp_path / "chart.png"
    Image.new("RGB", (240, 160), "white").save(chart)
    llm = FakeVisionClient()

    result = ChartReviewer(llm=llm, profile_name="openrouter_vision").review(
        chart,
        allowed_root=tmp_path,
    )

    assert result.verdict == "replot"
    assert result.reviewer == "deterministic"
    assert not llm.calls
