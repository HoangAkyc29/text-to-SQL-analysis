from __future__ import annotations

from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw

from project_core.domain.analysis.chart_validation import (
    ChartValidationLimits,
    source_data_fingerprint,
    validate_chart_artifact,
)


def _chart(path: Path, *, blank: bool = False) -> None:
    image = Image.new("RGB", (240, 160), "white")
    if not blank:
        draw = ImageDraw.Draw(image)
        draw.rectangle((30, 30, 100, 130), fill="navy")
        draw.rectangle((130, 70, 200, 130), fill="orange")
    image.save(path)


def test_valid_chart_and_source_fingerprint(tmp_path: Path) -> None:
    chart = tmp_path / "chart.png"
    _chart(chart)
    source = pd.DataFrame({"label": ["a", "b"], "value": [2, 1]})
    expected = source_data_fingerprint(source)

    result = validate_chart_artifact(
        chart,
        allowed_root=tmp_path,
        source_data=source,
        expected_source_fingerprint=expected,
    )

    assert result.verdict == "pass"
    assert result.source_fingerprint == expected
    assert result.artifact_path == str(chart.resolve())
    assert all(check.passed for check in result.deterministic_checks)
    assert result.source_consistency and result.source_consistency.valid


def test_rejects_path_outside_artifact_root(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside.png"
    _chart(outside)

    result = validate_chart_artifact(outside, allowed_root=allowed)

    assert result.verdict == "replot"
    assert "artifact_outside_allowed_root" in result.issues


def test_rejects_fake_and_blank_images(tmp_path: Path) -> None:
    fake = tmp_path / "fake.png"
    fake.write_text("not an image", encoding="utf-8")
    blank = tmp_path / "blank.png"
    _chart(blank, blank=True)

    fake_result = validate_chart_artifact(fake, allowed_root=tmp_path)
    blank_result = validate_chart_artifact(
        blank,
        allowed_root=tmp_path,
        limits=ChartValidationLimits(blank_variance_threshold=0.5),
    )

    assert fake_result.verdict == "replot"
    assert "image_not_decodable" in fake_result.issues
    assert blank_result.verdict == "replot"
    assert "image_appears_blank" in blank_result.issues


def test_source_fingerprint_mismatch_is_data_mismatch(tmp_path: Path) -> None:
    chart = tmp_path / "chart.png"
    _chart(chart)

    result = validate_chart_artifact(
        chart,
        allowed_root=tmp_path,
        source_data=[{"x": "a", "y": 1}],
        expected_source_fingerprint=source_data_fingerprint([{"x": "a", "y": 2}]),
    )

    assert result.verdict == "data_mismatch"
    assert "source_data_fingerprint_mismatch" in result.issues


def test_chart_columns_and_numeric_values_are_validated(tmp_path: Path) -> None:
    chart = tmp_path / "chart.png"
    _chart(chart)

    result = validate_chart_artifact(
        chart,
        allowed_root=tmp_path,
        source_data=[{"label": "a", "value": "not-a-number"}],
        chart_metadata={"x": "missing", "y": "value", "chart_kind": "bar"},
    )

    assert result.verdict == "data_mismatch"
    assert "source_x_column_missing" in result.issues
    assert "source_y_not_numeric" in result.issues
