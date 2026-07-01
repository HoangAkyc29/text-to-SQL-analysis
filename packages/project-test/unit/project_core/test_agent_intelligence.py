"""Unit tests for agent intelligence modules."""

from __future__ import annotations

import pytest

from project_core.domain.analysis.iv_analyzer import analyze_datasets
from project_core.domain.brief.merge import apply_data_feedback
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.feedback import DataFeedback
from project_core.domain.product.resolver import resolve_product_code
from project_core.ingest.attachments import ingest_file

pytestmark = pytest.mark.unit


def test_product_resolver_generates_probes():
    resolved = resolve_product_code("123456")
    assert resolved.probe_sql
    assert any("SKU_DEF" in q for q in resolved.probe_sql)


def test_apply_data_feedback_sets_exploration():
    brief = AnalysisBrief(intent="revenue")
    fb = DataFeedback(
        issue="empty_result",
        summary="no rows",
        diagnosis="needs_probe",
        suggested_intent_fix="widen time range",
    )
    updated = apply_data_feedback(brief, fb)
    assert updated.exploration_mode is True
    assert "widen" in updated.intent


def test_ingest_txt_file(tmp_path, monkeypatch):
    monkeypatch.setenv("ATTACHMENTS_DIR", str(tmp_path))
    src = ingest_file(session_id="s1", file_name="req.txt", content=b"Doanh thu SKU 123456")
    assert "Doanh thu" in src.text_excerpt


def test_iv_analyzer_empty_result(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    payload = analyze_datasets(
        brief=AnalysisBrief(intent="product 999", filters={"product_code": "999"}),
        manifest={"queries": []},
        profile={"row_count": 0},
        out_dir=str(out),
        max_steps=2,
    )
    assert payload["action"] == "data_feedback"
    assert payload["data_feedback"]["issue"] == "empty_result"
