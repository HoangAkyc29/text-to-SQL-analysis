"""Deterministic validation for chart artifacts and their source data."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

import pandas as pd
from PIL import Image, ImageStat, UnidentifiedImageError

from project_core.domain.contracts.plot_review import (
    PlotReviewCheck,
    PlotReviewIssue,
    PlotReviewResult,
    PlotSourceConsistency,
)


@dataclass(frozen=True)
class ChartValidationLimits:
    max_image_bytes: int = 8 * 1024 * 1024
    max_image_pixels: int = 20_000_000
    min_width: int = 64
    min_height: int = 64
    blank_variance_threshold: float = 0.5

    def __post_init__(self) -> None:
        if self.max_image_bytes <= 0 or self.max_image_pixels <= 0:
            raise ValueError("image limits must be positive")
        if self.min_width <= 0 or self.min_height <= 0:
            raise ValueError("minimum dimensions must be positive")
        if self.blank_variance_threshold < 0:
            raise ValueError("blank variance threshold cannot be negative")


@dataclass(frozen=True)
class ChartSourceValidation:
    valid: bool
    fingerprint: str | None
    row_count: int
    columns: tuple[str, ...]
    issues: tuple[str, ...] = ()


def resolve_contained_path(path: str | Path, allowed_root: str | Path) -> Path:
    """Resolve a path and reject traversal, symlinks, and paths outside the artifact root."""
    root = Path(allowed_root).resolve(strict=True)
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError("artifact_outside_allowed_root")
    return resolved


def source_data_fingerprint(source_data: Any) -> str:
    """Return a stable fingerprint for supported chart-source tabular data."""
    records = _normalise_source_data(source_data)
    encoded = json.dumps(
        records,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def validate_chart_source_data(
    source_data: Any,
    *,
    expected_fingerprint: str | None = None,
    x: str | None = None,
    y: str | None = None,
    chart_kind: str | None = None,
    max_points: int = 5_000,
    max_null_ratio: float = 0.5,
) -> ChartSourceValidation:
    issues: list[str] = []
    fingerprint: str | None = None
    records: list[dict[str, Any]] = []
    try:
        records = _normalise_source_data(source_data)
        fingerprint = source_data_fingerprint(records)
        if not records:
            issues.append("source_data_empty")
        elif not any(records):
            issues.append("source_data_has_no_columns")
        elif not any(value is not None for row in records for value in row.values()):
            issues.append("source_data_all_null")
        else:
            columns = set(records[0])
            if x and x not in columns:
                issues.append("source_x_column_missing")
            if y and y not in columns:
                issues.append("source_y_column_missing")
            if len(records) > max_points:
                issues.append("source_point_count_exceeded")
            if y and y in columns:
                numeric = pd.to_numeric(
                    pd.Series([row.get(y) for row in records]),
                    errors="coerce",
                )
                if not numeric.notna().any():
                    issues.append("source_y_not_numeric")
                elif float(numeric.isna().mean()) > max_null_ratio:
                    issues.append("source_y_null_ratio_exceeded")
                if chart_kind == "pie" and bool((numeric.dropna() < 0).any()):
                    issues.append("source_pie_has_negative_values")
            if x and x in columns and chart_kind in {"bar", "pie"}:
                cardinality = len({str(row.get(x)) for row in records})
                if cardinality > 100:
                    issues.append("source_cardinality_too_high")
    except (TypeError, ValueError, OSError):
        issues.append("source_data_invalid")

    if expected_fingerprint is not None:
        if not _valid_fingerprint(expected_fingerprint):
            issues.append("expected_source_fingerprint_invalid")
        elif fingerprint is not None and fingerprint != expected_fingerprint:
            issues.append("source_data_fingerprint_mismatch")

    columns = tuple(records[0]) if records else ()
    return ChartSourceValidation(
        valid=not issues,
        fingerprint=fingerprint,
        row_count=len(records),
        columns=columns,
        issues=tuple(issues),
    )


def validate_chart_artifact(
    artifact_path: str | Path,
    *,
    allowed_root: str | Path,
    source_data: Any | None = None,
    expected_source_fingerprint: str | None = None,
    chart_metadata: Mapping[str, Any] | None = None,
    artifact_role: Literal["chart", "uploaded_image", "image"] = "chart",
    limits: ChartValidationLimits | None = None,
) -> PlotReviewResult:
    """Fail-closed validation before a chart can be sent to a vision model."""
    limits = limits or ChartValidationLimits()
    issues: list[str] = []
    resolved: Path | None = None
    fingerprint: str | None = None

    try:
        resolved = resolve_contained_path(artifact_path, allowed_root)
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        issues.append(_safe_issue(exc, "invalid_artifact_path"))

    if resolved is not None:
        try:
            size = resolved.stat().st_size
            if size <= 0:
                issues.append("empty_image_file")
            elif size > limits.max_image_bytes:
                issues.append("image_file_too_large")
            _validate_decodable_image(resolved, limits, issues)
        except OSError:
            issues.append("image_file_unreadable")

    if source_data is not None:
        source_validation = validate_chart_source_data(
            source_data,
            expected_fingerprint=expected_source_fingerprint,
            x=str(chart_metadata["x"]) if chart_metadata and chart_metadata.get("x") else None,
            y=str(chart_metadata["y"]) if chart_metadata and chart_metadata.get("y") else None,
            chart_kind=(
                str(chart_metadata.get("chart_kind") or chart_metadata.get("kind")).lower()
                if chart_metadata
                and (chart_metadata.get("chart_kind") or chart_metadata.get("kind"))
                else None
            ),
        )
        fingerprint = source_validation.fingerprint
        issues.extend(source_validation.issues)
    elif expected_source_fingerprint is not None:
        issues.append("source_data_missing")

    if expected_source_fingerprint is not None and source_data is None:
        if not _valid_fingerprint(expected_source_fingerprint):
            issues.append("expected_source_fingerprint_invalid")

    data_issues = {
        "source_data_empty",
        "source_data_has_no_columns",
        "source_data_all_null",
        "source_data_invalid",
        "source_data_missing",
        "expected_source_fingerprint_invalid",
        "source_data_fingerprint_mismatch",
        "source_x_column_missing",
        "source_y_column_missing",
        "source_point_count_exceeded",
        "source_y_not_numeric",
        "source_y_null_ratio_exceeded",
        "source_pie_has_negative_values",
        "source_cardinality_too_high",
    }
    verdict = "data_mismatch" if any(issue in data_issues for issue in issues) else (
        "replot" if issues else "pass"
    )
    checks = _checks_for_issues(issues, source_data is not None)
    source_consistency = None
    if source_data is not None or expected_source_fingerprint is not None:
        source_consistency = PlotSourceConsistency(
            valid=not any(issue in data_issues for issue in issues),
            expected_fingerprint=(
                expected_source_fingerprint
                if expected_source_fingerprint and _valid_fingerprint(expected_source_fingerprint)
                else None
            ),
            actual_fingerprint=fingerprint,
            row_count=source_validation.row_count if source_data is not None else 0,
            columns=list(source_validation.columns) if source_data is not None else [],
            issues=[issue for issue in issues if issue in data_issues],
        )
    return PlotReviewResult(
        verdict=verdict,
        issues=issues,
        artifact_path=str(resolved) if resolved else str(artifact_path),
        source_fingerprint=fingerprint,
        reviewer="deterministic",
        vision_available=False,
        severity="error" if issues else "info",
        deterministic_checks=checks,
        structured_issues=[
            PlotReviewIssue(code=issue, message=issue.replace("_", " ")) for issue in issues
        ],
        source_consistency=source_consistency,
        artifact_role=artifact_role,
    )


def _validate_decodable_image(
    path: Path,
    limits: ChartValidationLimits,
    issues: list[str],
) -> None:
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            expected_format = {
                ".png": "PNG",
                ".jpg": "JPEG",
                ".jpeg": "JPEG",
                ".webp": "WEBP",
                ".gif": "GIF",
            }.get(path.suffix.lower())
            if expected_format is None or str(image.format).upper() != expected_format:
                issues.append("image_mime_suffix_mismatch")
            width, height = image.size
            if width < limits.min_width or height < limits.min_height:
                issues.append("image_dimensions_too_small")
            if width * height > limits.max_image_pixels:
                issues.append("image_pixel_limit_exceeded")
                return
            image.load()
            grayscale = image.convert("L")
            variance = float(ImageStat.Stat(grayscale).var[0])
            if variance <= limits.blank_variance_threshold:
                issues.append("image_appears_blank")
    except (DecompressionBombError, UnidentifiedImageError, OSError, SyntaxError, ValueError):
        issues.append("image_not_decodable")


def _normalise_source_data(source_data: Any) -> list[dict[str, Any]]:
    if isinstance(source_data, (str, Path)):
        path = Path(source_data)
        if path.suffix.lower() == ".parquet":
            frame = pd.read_parquet(path)
        elif path.suffix.lower() == ".csv":
            frame = pd.read_csv(path)
        else:
            raise ValueError("unsupported source data file")
        return _frame_records(frame)
    if isinstance(source_data, pd.DataFrame):
        return _frame_records(source_data)
    if isinstance(source_data, Mapping):
        source_data = [source_data]
    if isinstance(source_data, Sequence) and not isinstance(source_data, (bytes, bytearray, str)):
        records: list[dict[str, Any]] = []
        for row in source_data:
            if not isinstance(row, Mapping):
                raise TypeError("source rows must be mappings")
            records.append({str(key): _json_scalar(value) for key, value in row.items()})
        return records
    raise TypeError("unsupported source data")


def _frame_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame.columns.has_duplicates:
        raise ValueError("duplicate source columns")
    records: list[dict[str, Any]] = []
    for row in frame.itertuples(index=False, name=None):
        records.append(
            {str(column): _json_scalar(value) for column, value in zip(frame.columns, row, strict=True)}
        )
    return records


def _json_scalar(value: Any) -> Any:
    if value is None or value is pd.NA:
        return None
    if hasattr(value, "item") and not isinstance(value, (str, bytes, bytearray)):
        try:
            value = value.item()
        except (ValueError, AttributeError):
            pass
    if isinstance(value, float):
        if math.isnan(value):
            return None
        if not math.isfinite(value):
            raise ValueError("non-finite source value")
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (str, int, bool)):
        return value
    if pd.isna(value):
        return None
    raise TypeError(f"unsupported source value: {type(value).__name__}")


def _valid_fingerprint(value: str) -> bool:
    if not value.startswith("sha256:") or len(value) != 71:
        return False
    return all(char in "0123456789abcdef" for char in value[7:])


def _safe_issue(exc: Exception, fallback: str) -> str:
    message = str(exc)
    return message if message in {"artifact_outside_allowed_root"} else fallback


def _checks_for_issues(issues: list[str], has_source: bool) -> list[PlotReviewCheck]:
    groups = {
        "artifact_contained": {"invalid_artifact_path", "artifact_outside_allowed_root"},
        "image_size": {"empty_image_file", "image_file_too_large"},
        "image_decodable": {"image_file_unreadable", "image_not_decodable"},
        "image_mime": {"image_mime_suffix_mismatch"},
        "image_dimensions": {"image_dimensions_too_small"},
        "image_pixels": {"image_pixel_limit_exceeded"},
        "image_variance": {"image_appears_blank"},
    }
    if has_source:
        groups["source_data"] = {
            "source_data_empty",
            "source_data_has_no_columns",
            "source_data_all_null",
            "source_data_invalid",
            "source_data_fingerprint_mismatch",
            "expected_source_fingerprint_invalid",
            "source_x_column_missing",
            "source_y_column_missing",
            "source_point_count_exceeded",
            "source_y_not_numeric",
            "source_y_null_ratio_exceeded",
            "source_pie_has_negative_values",
            "source_cardinality_too_high",
        }
    issue_set = set(issues)
    return [
        PlotReviewCheck(
            code=code,
            passed=not bool(issue_set & failures),
            detail=", ".join(sorted(issue_set & failures)) or None,
        )
        for code, failures in groups.items()
    ]


DecompressionBombError = Image.DecompressionBombError
