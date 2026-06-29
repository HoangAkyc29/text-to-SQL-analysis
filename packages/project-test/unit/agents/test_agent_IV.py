"""Agent IV (data-analyst) sandbox handoff outputs."""

from __future__ import annotations

import json

import pytest

from data_analyst.service import DataAnalystService

pytestmark = pytest.mark.unit


def _svc() -> DataAnalystService:
    return object.__new__(DataAnalystService)


def test_IV_complete_with_rows(decision_ctx):
    ctx = decision_ctx(
        goal=json.dumps(
            {
                "dataset_manifest": {"queries": [{"path": "data/artifacts/t/raw/q.parquet"}]},
                "result_profile": {"row_count": 50},
            }
        )
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["action"] == "complete"
    assert payload["headline_metrics"]["row_count"] == 50


def test_IV_data_feedback_when_empty(decision_ctx):
    ctx = decision_ctx(
        goal=json.dumps({"dataset_manifest": {"queries": []}, "result_profile": {"row_count": 0}})
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["action"] == "data_feedback"
    assert payload["data_feedback"]["needs_sql_retry"] is True


def test_IV_artifact_paths_map_raw_to_out(decision_ctx):
    ctx = decision_ctx(
        goal=json.dumps(
            {
                "dataset_manifest": {"queries": [{"path": "data/artifacts/t/raw/query_0.parquet"}]},
                "result_profile": {"row_count": 3},
            }
        )
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert any("out" in p for p in payload["artifact_paths"])
