from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SKILLS_ROOT = ROOT / "agents"


def test_active_agent_skills_do_not_embed_trial_constants():
    patterns = {
        "document_code_recipe": re.compile(
            r"TRANS_CODE\s*[=:]?\s*['\"]?113\b",
            re.IGNORECASE,
        ),
        "trial_threshold": re.compile(r"\b(?:600k|600[.]000|600000)\b", re.IGNORECASE),
        "trial_product": re.compile(r"\b0030(?:344|348|355)\b"),
    }
    violations: list[str] = []
    for path in SKILLS_ROOT.glob("*/src/*/skills/**/*"):
        if path.suffix.lower() not in {".md", ".txt", ".yaml", ".yml"}:
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in patterns.items():
            if pattern.search(text):
                violations.append(f"{path.relative_to(ROOT)}:{label}")
    assert violations == []
