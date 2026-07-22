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


class BriefRequirement(BaseModel):
    """One auditable obligation extracted from the user's request."""

    requirement_id: str
    kind: Literal["metric", "dimension", "filter", "time", "ranking", "output"]
    key: str
    source: Literal["explicit", "inferred", "carried"] = "explicit"
    required: bool = True
    evidence_quote: str = ""
    value: Any = None


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
    retrieval_facets: list[str] = Field(default_factory=list)
    external_sources: list[ExternalSource] = Field(default_factory=list)
    plan: AnalysisPlan | None = None
    requirements: list[BriefRequirement] = Field(default_factory=list)

    def blocking_requirements(self, kind: str | None = None) -> list[BriefRequirement]:
        """Return explicit must-have requirements; preserve legacy callers."""
        selected = [
            item
            for item in self.requirements
            if item.required
            and item.source in {"explicit", "carried"}
            and (kind is None or item.kind == kind)
        ]
        if self.requirements or kind is None:
            return selected
        # Briefs created directly by tests/internal callers predate requirement
        # provenance. Their declared fields remain blocking for compatibility.
        if kind == "metric":
            return [
                BriefRequirement(
                    requirement_id=f"metric:{index}",
                    kind="metric",
                    key=str(value),
                    value=value,
                )
                for index, value in enumerate(self.metrics)
            ]
        if kind == "dimension":
            return [
                BriefRequirement(
                    requirement_id=f"dimension:{index}",
                    kind="dimension",
                    key=str(value),
                    value=value,
                )
                for index, value in enumerate(self.dimensions)
            ]
        if kind == "filter":
            return [
                BriefRequirement(
                    requirement_id=f"filter:{key}",
                    kind="filter",
                    key=str(key),
                    value=value,
                )
                for key, value in self.filters.items()
            ]
        return []


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
    verification: dict[str, Any] = Field(default_factory=dict)
    deliverables: list[dict[str, Any]] = Field(default_factory=list)


class RouterIngressResult(BaseModel):
    route: Literal["chitchat", "analysis", "confirm_cancel", "wait"]
    user_message: str = ""
    brief: AnalysisBrief | None = None
    satisfaction_signal: SatisfactionSignal | None = None
    dialogue_act: (
        Literal[
            "new_request",
            "follow_up_same_task",
            "revise_and_rerun",
            "correction_only",
            "topic_switch",
            "chitchat",
            "satisfaction",
        ]
        | None
    ) = None
