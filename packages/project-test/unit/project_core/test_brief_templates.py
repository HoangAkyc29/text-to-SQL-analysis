"""Brief templates loader."""

from __future__ import annotations

from project_core.domain.brief.templates import brief_templates_excerpt


def test_brief_templates_excerpt_not_empty():
    text = brief_templates_excerpt()
    assert "VIP monthly chart" in text
    assert "Store revenue ranking" in text
    assert len(text) > 200
