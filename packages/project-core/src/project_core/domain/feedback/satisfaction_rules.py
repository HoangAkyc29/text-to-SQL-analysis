from __future__ import annotations

import re
from typing import Any

_POSITIVE = re.compile(r"(cảm ơn|chuẩn|đúng rồi|ok|tốt|hay)", re.I)
_NEGATIVE = re.compile(r"(sai rồi|số lạ|không phải|tính lại|sai)", re.I)
_REPHRASE = re.compile(r"(tính lại|không phải thế|làm lại)", re.I)


def detect_satisfaction(text: str) -> dict[str, Any] | None:
    if _REPHRASE.search(text):
        return {"sentiment": "negative", "confidence": 0.8, "intent": "rephrase_retry"}
    if _NEGATIVE.search(text):
        return {"sentiment": "negative", "confidence": 0.8}
    if _POSITIVE.search(text):
        return {"sentiment": "positive", "confidence": 0.85}
    return None
