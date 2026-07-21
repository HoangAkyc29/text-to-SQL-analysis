from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


PlotReviewVerdict = Literal["pass", "replot", "data_mismatch", "unavailable"]


class PlotReviewIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=500)


class PlotReviewCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1, max_length=64)
    passed: bool
    detail: str | None = Field(default=None, max_length=500)


class PlotFixArgs(BaseModel):
    """Safe declarative plot arguments; never executable plotting code."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["bar", "line", "pie", "hist", "scatter"] | None = None
    title: str | None = Field(default=None, max_length=200)
    x: str | None = Field(default=None, max_length=128)
    y: str | None = Field(default=None, max_length=128)
    hue: str | None = Field(default=None, max_length=128)
    orientation: Literal["vertical", "horizontal"] | None = None
    width: float | None = Field(default=None, ge=4, le=24)
    height: float | None = Field(default=None, ge=3, le=18)
    rotate_x_labels: int | None = Field(default=None, ge=0, le=90)
    show_legend: bool | None = None


class PlotSourceConsistency(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valid: bool
    expected_fingerprint: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")
    actual_fingerprint: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")
    row_count: int = Field(default=0, ge=0)
    columns: list[str] = Field(default_factory=list, max_length=200)
    issues: list[str] = Field(default_factory=list, max_length=12)


class PlotReviewResult(BaseModel):
    """Bounded, machine-readable result of deterministic and vision review."""

    model_config = ConfigDict(extra="forbid")

    verdict: PlotReviewVerdict
    issues: list[str] = Field(default_factory=list)
    suggested_plot_fix: str | None = Field(default=None, max_length=500)
    artifact_path: str | None = None
    source_fingerprint: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")
    reviewer: Literal["deterministic", "vision"] = "deterministic"
    vision_available: bool = False
    artifact_role: Literal["chart", "uploaded_image", "image"] = "chart"
    severity: Literal["info", "warning", "error"] = "info"
    deterministic_checks: list[PlotReviewCheck] = Field(default_factory=list, max_length=32)
    structured_issues: list[PlotReviewIssue] = Field(default_factory=list, max_length=12)
    fix_args: PlotFixArgs | None = None
    source_consistency: PlotSourceConsistency | None = None
    review_attempts: int = Field(default=0, ge=0, le=10)

    @field_validator("issues")
    @classmethod
    def _bound_issues(cls, value: list[str]) -> list[str]:
        if len(value) > 12:
            raise ValueError("at most 12 review issues are allowed")
        cleaned: list[str] = []
        for issue in value:
            text = str(issue).strip()
            if not text:
                continue
            if len(text) > 500:
                raise ValueError("review issue exceeds 500 characters")
            if "```" in text:
                raise ValueError("free-form code is not allowed in review issues")
            cleaned.append(text)
        return cleaned

    @field_validator("suggested_plot_fix")
    @classmethod
    def _reject_code_fix(cls, value: str | None) -> str | None:
        if value is not None and "```" in value:
            raise ValueError("free-form code is not allowed in plot fixes")
        return value
