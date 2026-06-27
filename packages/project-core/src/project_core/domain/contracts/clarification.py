from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from project_core.domain.contracts.brief import AnalysisBrief


class ClarificationOption(BaseModel):
    id: str
    label: str
    brief_value: dict[str, Any] | None = None


class ClarificationQuestion(BaseModel):
    id: str
    prompt: str
    options: list[ClarificationOption]
    allow_multiple: bool = False
    maps_to_brief_field: str


class ClarificationRequest(BaseModel):
    source_agent: Literal["II"] = "II"
    reason: str
    partial_brief: AnalysisBrief
    trigger_context: Literal[
        "initial", "after_policy", "after_risk", "after_data_feedback"
    ] = "initial"
    questions: list[ClarificationQuestion]


class ClarificationAnswer(BaseModel):
    question_id: str
    selected_option_id: str
    other_text: str | None = None
    evidence: str | None = None


class ClarificationReply(BaseModel):
    analysis_id: str
    answers: list[ClarificationAnswer]


class ClarificationBridgeResult(BaseModel):
    action: Literal["resolve_from_transcript", "ask_user"]
    answers: list[ClarificationAnswer] = Field(default_factory=list)
    confidence: float = 0.0
    user_message: str | None = None
    clarification: ClarificationRequest | None = None
