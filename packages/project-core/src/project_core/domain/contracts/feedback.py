from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


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
    # Optional ONLY for legacy/stub paths. Production IV must leave this empty —
    # Agent II writes probe SQL itself (no recipe injection).
    suggested_sql: str = ""
    priority: int = 1

    @field_validator("suggested_sql")
    @classmethod
    def strip_production_sql_recipe(cls, value: str) -> str:
        """SQL suggestions are permitted only inside the explicit stub gate."""
        if os.getenv("ALLOW_LLM_STUB") != "1":
            return ""
        return value


class DomainEvidence(BaseModel):
    """Auditable evidence for a reusable declarative domain fact."""

    evidence_id: str = ""
    source_kind: Literal[
        "user_statement",
        "clarification",
        "data_observation",
        "dictionary",
        "case_study",
        "external_document",
        "agent_inference",
    ] = "data_observation"
    source_ref: str = ""
    quote: str = ""
    actor_id: str = ""
    trace_id: str = ""
    schema_links: list[dict[str, str]] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    independent_group: str = ""
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DomainRuleCandidate(BaseModel):
    rule_id: str = ""
    fact_type: Literal["definition", "formula", "classification", "relationship", "constraint"] = (
        "definition"
    )
    scope: Literal["user", "tenant", "global"] = "user"
    actor_id: str = ""
    tenant_id: str = ""
    statement: str = ""
    evidence_trace_ids: list[str] = Field(default_factory=list)
    evidence: list[DomainEvidence] = Field(default_factory=list)
    schema_links: list[dict[str, str]] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    authority: Literal["requester", "domain_owner", "admin", "system"] = "requester"
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    supersedes_rule_id: str | None = None

    @field_validator("scope", mode="before")
    @classmethod
    def normalize_legacy_scope(cls, value: Any) -> str:
        text = str(value or "").strip().lower()
        if text == "general":
            return "global"
        return text or "user"


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
