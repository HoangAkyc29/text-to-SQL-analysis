from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from project_core.domain.contracts.analysis_plan import AnalysisPlan
from project_core.domain.contracts.external_source import ExternalSource
from project_core.domain.contracts.feedback import SatisfactionSignal


class TimeRange(BaseModel):
    start: str | None = None
    end: str | None = None
    grain: str | None = None


class AnalysisBrief(BaseModel):
    intent: str = ""
    metrics: list[str] = Field(default_factory=list)
    dimensions: list[str] = Field(default_factory=list)
    filters: dict[str, Any] = Field(default_factory=dict)
    time_range: TimeRange = Field(default_factory=TimeRange)
    output_format: list[str] = Field(default_factory=list)
    chart_spec: dict[str, Any] | None = None
    exploration_mode: bool = False
    user_knowledge_level: Literal["expert", "unknown"] = "expert"
    probe_hints: list[str] = Field(default_factory=list)
    external_sources: list[ExternalSource] = Field(default_factory=list)
    plan: AnalysisPlan | None = None


class IntentSlice(BaseModel):
    metrics: list[str] = Field(default_factory=list)
    dimensions: list[str] = Field(default_factory=list)
    filters: dict[str, Any] = Field(default_factory=dict)
    time_range: TimeRange = Field(default_factory=TimeRange)
    output_format: list[str] = Field(default_factory=list)

    @classmethod
    def from_brief(cls, brief: AnalysisBrief) -> IntentSlice:
        return cls(
            metrics=list(brief.metrics),
            dimensions=list(brief.dimensions),
            filters=dict(brief.filters),
            time_range=brief.time_range.model_copy(),
            output_format=list(brief.output_format),
        )


class TechnicalSummary(BaseModel):
    outcome: str
    headline_metrics: dict[str, Any] = Field(default_factory=dict)
    artifact_urls: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    empty_reason: str | None = None
    coverage: dict[str, Any] = Field(default_factory=dict)


class RouterIngressResult(BaseModel):
    route: Literal["chitchat", "analysis", "confirm_cancel", "wait"]
    user_message: str = ""
    brief: AnalysisBrief | None = None
    satisfaction_signal: SatisfactionSignal | None = None
