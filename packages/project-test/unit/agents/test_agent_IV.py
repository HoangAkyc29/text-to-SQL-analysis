"""Agent IV (data-analyst) sandbox handoff outputs."""

from __future__ import annotations

import json

import pytest

from data_analyst.service import DataAnalystService

pytestmark = pytest.mark.unit


def _svc() -> DataAnalystService:
    return object.__new__(DataAnalystService)


def test_IV_complete_with_rows(decision_ctx, sample_parquet, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    ctx = decision_ctx(
        goal=json.dumps(
            {
                "dataset_manifest": {"queries": [{"path": str(sample_parquet), "row_count": 2}]},
                "result_profile": {"row_count": 50},
                "out_dir": str(out),
            }
        )
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["action"] in {"complete", "partial"}
    assert payload["headline_metrics"]["row_count"] == 50
    assert "coverage" in payload


def test_IV_data_feedback_when_empty(decision_ctx):
    ctx = decision_ctx(
        goal=json.dumps({"dataset_manifest": {"queries": []}, "result_profile": {"row_count": 0}})
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["action"] == "data_feedback"
    assert payload["data_feedback"]["needs_sql_retry"] is True


def test_IV_artifact_paths_map_raw_to_out(decision_ctx, sample_parquet, tmp_path):
    out = tmp_path / "artifacts" / "t" / "out"
    out.mkdir(parents=True)
    ctx = decision_ctx(
        goal=json.dumps(
            {
                "dataset_manifest": {"queries": [{"path": str(sample_parquet), "row_count": 3}]},
                "result_profile": {"row_count": 3},
                "out_dir": str(out),
            }
        )
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["action"] in {"complete", "partial"}
    assert payload.get("artifact_paths")
    assert "coverage" in payload
