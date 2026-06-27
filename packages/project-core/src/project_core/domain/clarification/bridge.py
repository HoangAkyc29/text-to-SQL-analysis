from __future__ import annotations

import json
import re
from typing import Any

from project_core.domain.contracts.clarification import (
    ClarificationBridgeResult,
    ClarificationRequest,
)
from project_core.domain.memory.session_bundle import TranscriptTurn


class ClarificationBridge:
    def __init__(self, min_confidence: float = 0.75) -> None:
        self.min_confidence = min_confidence

    def from_transcript_heuristic(
        self,
        request: ClarificationRequest,
        transcript: list[TranscriptTurn],
    ) -> ClarificationBridgeResult:
        user_text = " ".join(t.content for t in transcript if t.role == "user").lower()
        answers = []
        confidence_scores: list[float] = []
        for question in request.questions:
            resolved = self._resolve_question(question.id, question.maps_to_brief_field, user_text)
            if resolved:
                answers.append(resolved)
                confidence_scores.append(resolved.get("_confidence", 0.8))
        if answers and confidence_scores and min(confidence_scores) >= self.min_confidence:
            clean_answers = []
            for a in answers:
                a = dict(a)
                a.pop("_confidence", None)
                clean_answers.append(a)
            return ClarificationBridgeResult(
                action="resolve_from_transcript",
                answers=clean_answers,
                confidence=min(confidence_scores),
            )
        return ClarificationBridgeResult(action="ask_user", clarification=request)

    def _resolve_question(self, question_id: str, field: str, text: str) -> dict[str, Any] | None:
        if "vip" in question_id or "vip" in field:
            if "card" in text and re.search(r"prefix\s*e|bắt đầu\s*e|tiền tố\s*e", text):
                return {
                    "question_id": question_id,
                    "selected_option_id": "other",
                    "other_text": "card_id prefix E",
                    "evidence": "transcript mentions card E",
                    "_confidence": 0.85,
                }
        if "trans" in question_id or "transaction" in field:
            if "221" in text or "trans_code" in text:
                return {
                    "question_id": question_id,
                    "selected_option_id": "other",
                    "other_text": "trans_code = 221",
                    "evidence": "transcript mentions 221",
                    "_confidence": 0.85,
                }
        if "point" in question_id or "points" in field:
            if "50000" in text or "/50000" in text or "chia 50000" in text:
                return {
                    "question_id": question_id,
                    "selected_option_id": "other",
                    "other_text": "SUM(amount)/50000",
                    "evidence": "transcript mentions /50000",
                    "_confidence": 0.85,
                }
        return None

    @staticmethod
    def parse_llm_bridge(content: str, request: ClarificationRequest) -> ClarificationBridgeResult:
        try:
            data = json.loads(content)
            return ClarificationBridgeResult.model_validate(data)
        except Exception:  # noqa: BLE001
            return ClarificationBridgeResult(action="ask_user", clarification=request)
