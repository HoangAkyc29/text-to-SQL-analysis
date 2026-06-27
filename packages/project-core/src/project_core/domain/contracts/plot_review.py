from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PlotReviewResult(BaseModel):
    verdict: Literal["pass", "replot", "data_mismatch"]
    issues: list[str] = Field(default_factory=list)
    suggested_plot_fix: str | None = None
    artifact_path: str | None = None
