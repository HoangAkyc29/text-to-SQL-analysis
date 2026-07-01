from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class BriefAlignment(BaseModel):
    metric_from_brief: str | None = None
    dimensions_from_brief: list[str] = Field(default_factory=list)
    what_brief_needed: str = ""
    what_data_showed: str = ""


class ExpectedVsObserved(BaseModel):
    aspect: str
    expected: str
    observed: str
    source: str = ""


class MissingForBrief(BaseModel):
    brief_field: str
    reason: str


class ProbeRequest(BaseModel):
    table: str
    purpose: str
    suggested_sql: str
    priority: int = 1


class DomainRuleCandidate(BaseModel):
    rule_id: str = ""
    scope: str = ""
    statement: str = ""
    evidence_trace_ids: list[str] = Field(default_factory=list)


class DataFeedback(BaseModel):
    needs_sql_retry: bool = True
    issue: str
    summary: str
    diagnosis: Literal["solvable", "needs_probe", "impossible", "needs_user_clarify"] = "solvable"
    affected_columns: list[str] = Field(default_factory=list)
    brief_alignment: BriefAlignment | None = None
    expected_vs_observed: list[ExpectedVsObserved] = Field(default_factory=list)
    missing_for_brief: list[MissingForBrief] = Field(default_factory=list)
    suggested_intent_fix: str = ""
    evidence_refs: list[str] = Field(default_factory=list)
    probe_requests: list[ProbeRequest] = Field(default_factory=list)
    confirmed_rules: list[DomainRuleCandidate] = Field(default_factory=list)


class SatisfactionSignal(BaseModel):
    applies_to_trace_id: str | None = None
    sentiment: Literal["positive", "negative", "neutral", "unknown"] = "unknown"
    confidence: float = 0.0
    failure_mode: str | None = None
    evidence: str = ""


class FeedbackRecord(BaseModel):
    id: str
    trace_id: str
    analysis_id: str
    session_id: str
    actor_id: str
    source: Literal["explicit", "conversational", "behavioral"]
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float
    failure_mode: str | None = None
    evidence: str = ""


class BehavioralSignal(BaseModel):
    session_id: str
    signal_type: Literal["re_ask", "download", "abandon"]
    weight: float = 0.5
    trace_id: str | None = None
