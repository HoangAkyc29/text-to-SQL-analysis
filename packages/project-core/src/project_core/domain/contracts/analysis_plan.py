from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class AnalysisSubtask(BaseModel):
    id: str
    intent: str
    metrics: list[str] = Field(default_factory=list)
    dimensions: list[str] = Field(default_factory=list)
    filters: dict[str, Any] = Field(default_factory=dict)
    status: Literal["pending", "done", "skipped", "failed"] = "pending"
    dataset_query_index: int | None = None


class AnalysisPlan(BaseModel):
    subtasks: list[AnalysisSubtask] = Field(default_factory=list)
    is_decomposed: bool = False


class RecipeParam(BaseModel):
    name: str
    type: str = "string"
    default: Any = None
    enum: list[str] = Field(default_factory=list)


class RecipeStep(BaseModel):
    step_id: str
    name: str = ""
    script_template: str = ""
    source_tool_id: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    param_schema: list[RecipeParam] = Field(default_factory=list)
    dataset_role: str = "primary"
    status: Literal["reuse", "generated", "inline"] = "generated"


class RecipeCandidate(BaseModel):
    tool_id: str
    name: str
    intent_pattern: str
    score: float
    matched_aspects: list[str] = Field(default_factory=list)
    missing_aspects: list[str] = Field(default_factory=list)
    steps: list[RecipeStep] = Field(default_factory=list)
    script_template: str = ""
    param_schema: list[RecipeParam] = Field(default_factory=list)


class ExecutionStepPlan(BaseModel):
    subtask_id: str
    step: RecipeStep
    dataset_path: str = ""
    candidate_tool_id: str | None = None
    match_score: float = 0.0


class ExecutionCoverage(BaseModel):
    diagnosis: Literal["full", "partial", "none"] = "none"
    reused: list[str] = Field(default_factory=list)
    generated: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    subtask_status: dict[str, str] = Field(default_factory=dict)
