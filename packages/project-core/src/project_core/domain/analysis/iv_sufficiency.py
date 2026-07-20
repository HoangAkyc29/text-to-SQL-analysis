"""Deterministic sufficiency checks before Agent IV finalizes.

Catches empty/unusable deliverables that the LLM might otherwise mark complete,
so the pipeline can emit ``data_feedback`` (retry II) instead of a hollow answer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.feedback import DataFeedback, ExpectedVsObserved, MissingForBrief


@dataclass(frozen=True)
class SufficiencyResult:
    sufficient: bool
    force_feedback: bool
    gaps: list[str] = field(default_factory=list)
    issue: str = ""
    summary: str = ""


def _norm_formats(output_format: list[str] | None) -> set[str]:
    return {str(x).strip().lower() for x in (output_format or []) if str(x).strip()}


def _is_chart_path(path: str) -> bool:
    return Path(path).suffix.lower() in {".png", ".jpg", ".jpeg", ".svg", ".webp"}


def _is_excel_path(path: str) -> bool:
    return Path(path).suffix.lower() in {".xlsx", ".xls", ".xlsm"}


def assess_sufficiency(
    brief: AnalysisBrief,
    *,
    row_count: int,
    artifacts: list[str],
    chart_artifacts: list[str] | None = None,
    excel_artifacts: list[str] | None = None,
    headline_metrics: dict[str, Any] | None = None,
    claimed_status: str = "complete",
) -> SufficiencyResult:
    """Return whether IV outputs meet the brief well enough to finalize.

    ``force_feedback`` means Agent II should re-plan SQL (or provide better grain),
    not that IV merely needs another sandbox step.
    """
    arts = [a for a in artifacts if a]
    charts = list(chart_artifacts or []) or [a for a in arts if _is_chart_path(a)]
    excels = list(excel_artifacts or []) or [a for a in arts if _is_excel_path(a)]
    tabular = [a for a in arts if a not in charts and a not in excels]
    formats = _norm_formats(brief.output_format)
    metrics = headline_metrics or {}
    gaps: list[str] = []

    if int(row_count or 0) <= 0:
        return SufficiencyResult(
            sufficient=False,
            force_feedback=True,
            gaps=["empty_result"],
            issue="empty_result",
            summary="Không có dòng dữ liệu để phân tích theo yêu cầu.",
        )

    if not arts:
        return SufficiencyResult(
            sufficient=False,
            force_feedback=True,
            gaps=["missing_artifacts"],
            issue="missing_artifacts",
            summary="Phân tích kết thúc nhưng không có file kết quả (CSV/Excel/biểu đồ).",
        )

    if formats & {"chart", "plot", "graph"} and not charts:
        gaps.append("missing_chart")
    if formats & {"excel", "xlsx", "spreadsheet"} and not excels:
        gaps.append("missing_excel")

    # Brief lists metrics but we have neither a metric value nor a tabular export.
    brief_metrics = [m for m in (brief.metrics or []) if str(m).strip()]
    metric_keys = {str(k).lower() for k in metrics if k and str(k).lower() != "row_count"}
    if brief_metrics and not metric_keys and not tabular and not excels:
        gaps.append("missing_metric_deliverable")

    if not gaps:
        return SufficiencyResult(sufficient=True, force_feedback=False)

    # Format-only gaps (have usable table/excel) → partial OK, do not bounce to II.
    format_only = set(gaps) <= {"missing_chart", "missing_excel"}
    if format_only and (tabular or excels or charts):
        return SufficiencyResult(
            sufficient=claimed_status == "partial",
            force_feedback=False,
            gaps=gaps,
            issue="partial_coverage",
            summary="Có kết quả bảng nhưng thiếu định dạng đầu ra theo brief: " + ", ".join(gaps),
        )

    return SufficiencyResult(
        sufficient=False,
        force_feedback=True,
        gaps=gaps,
        issue="insufficient_deliverable",
        summary="Kết quả chưa đủ để trả lời yêu cầu: " + ", ".join(gaps),
    )


def insufficiency_data_feedback(
    brief: AnalysisBrief,
    result: SufficiencyResult,
    *,
    row_count: int,
    artifacts: list[str],
) -> dict[str, Any]:
    """Build an AnalystResponse-shaped ``data_feedback`` payload."""
    expected = "artifacts + metrics covering brief intent"
    observed = f"row_count={row_count}, artifacts={len(artifacts)}, gaps={result.gaps}"
    fb = DataFeedback(
        needs_sql_retry=True,
        issue=result.issue or "insufficient_deliverable",
        summary=result.summary or "Kết quả chưa đủ deliverable",
        diagnosis="solvable",
        suggested_intent_fix=brief.intent,
        expected_vs_observed=[
            ExpectedVsObserved(aspect="deliverable", expected=expected, observed=observed)
        ],
        missing_for_brief=[
            MissingForBrief(brief_field=g, reason="not satisfied by current SQL/result set")
            for g in result.gaps
        ],
    )
    payload: dict[str, Any] = {
        "action": "data_feedback",
        "data_feedback": fb.model_dump(),
        "caveats": list(result.gaps)[:8],
    }
    if artifacts:
        payload["artifact_paths"] = list(artifacts)
    return payload


def candidate_score(
    *,
    action: str,
    row_count: int,
    artifact_count: int,
    has_insight: bool = False,
) -> int:
    """Rank a pipeline attempt for best-effort delivery after retries exhaust."""
    score = 0
    act = (action or "").lower()
    if act == "complete":
        score += 200
    elif act == "partial":
        score += 120
    elif act == "data_feedback":
        score += 40
    score += min(int(row_count or 0), 500)
    score += int(artifact_count or 0) * 25
    if has_insight:
        score += 15
    return score
