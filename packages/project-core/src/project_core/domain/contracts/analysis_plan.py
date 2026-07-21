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


class RecipeDatasetContract(BaseModel):
    role: str
    required_columns: list[str] = Field(default_factory=list)
    optional_columns: list[str] = Field(default_factory=list)
    dtypes: dict[str, str] = Field(default_factory=dict)
    grain: list[str] = Field(default_factory=list)
    source_kind: str | None = None


class RecipeVerificationContract(BaseModel):
    required_ops: list[str] = Field(default_factory=lambda: ["validate_export"])
    require_primary_artifact: bool = True
    require_current_revision: bool = True
    source_run_verified: bool = False
    replay_verified: bool = False


class RecipeStep(BaseModel):
    """Legacy script step and/or catalog op step.

    Op-chain recipes set ``op_id`` (+ optional ``args``/``dataset``/``save_as``).
    Script recipes use ``script_template``.
    """

    step_id: str = ""
    name: str = ""
    script_template: str = ""
    op_id: str | None = None
    args: dict[str, Any] = Field(default_factory=dict)
    dataset: str | None = None
    save_as: str | None = None
    source_tool_id: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    param_schema: list[RecipeParam] = Field(default_factory=list)
    dataset_role: str = "primary"
    status: Literal["reuse", "generated", "inline"] = "generated"

    def model_post_init(self, __context: Any) -> None:
        if not self.step_id:
            if self.op_id:
                self.step_id = f"op-{self.op_id}"
            elif self.script_template:
                self.step_id = "script-main"


class RecipeCandidate(BaseModel):
    tool_id: str
    name: str
    intent_pattern: str
    score: float
    matched_aspects: list[str] = Field(default_factory=list)
    missing_aspects: list[str] = Field(default_factory=list)
    steps: list[RecipeStep] = Field(default_factory=list)
    op_chain: list[dict[str, Any]] = Field(default_factory=list)
    script_template: str = ""
    param_schema: list[RecipeParam] = Field(default_factory=list)
    dataset_contracts: list[RecipeDatasetContract] = Field(default_factory=list)
    verification_contract: RecipeVerificationContract = Field(
        default_factory=RecipeVerificationContract
    )
    compatibility_version: int = 2
    compatibility_status: Literal["compatible", "incompatible", "unknown"] = "unknown"
    rejection_reasons: list[str] = Field(default_factory=list)
    dataset_bindings: dict[str, str] = Field(default_factory=dict)


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
