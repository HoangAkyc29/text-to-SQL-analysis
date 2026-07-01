from __future__ import annotations

from project_core.paths import ROOT


def brief_templates_excerpt(*, max_chars: int = 4000) -> str:
    path = ROOT / "data_dictionary" / "brief_templates.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")[:max_chars]
