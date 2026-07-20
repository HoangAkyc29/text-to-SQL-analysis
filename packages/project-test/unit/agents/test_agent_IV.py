"""Agent IV (data-analyst) sandbox handoff outputs."""

from __future__ import annotations

import json

import pytest

from data_analyst.service import DataAnalystService
from project_core.domain.access.acl import build_permissions_snapshot

pytestmark = pytest.mark.unit

_PERMS = build_permissions_snapshot("user-1", "hq_analyst").model_dump(mode="json")


def _svc() -> DataAnalystService:
    return object.__new__(DataAnalystService)


def _goal(payload: dict) -> str:
    return json.dumps({**payload, "permissions": _PERMS})


def test_IV_complete_with_rows(decision_ctx, sample_parquet, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    ctx = decision_ctx(
        goal=_goal(
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
        goal=_goal({"dataset_manifest": {"queries": []}, "result_profile": {"row_count": 0}})
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["action"] == "data_feedback"
    assert payload["data_feedback"]["needs_sql_retry"] is True


def test_IV_artifact_paths_map_raw_to_out(decision_ctx, sample_parquet, tmp_path, monkeypatch):
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path / "artifacts"))
    out = tmp_path / "artifacts" / "t" / "out"
    out.mkdir(parents=True)
    ctx = decision_ctx(
        goal=_goal(
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


def test_IV_denied_without_permissions(decision_ctx):
    ctx = decision_ctx(
        goal=json.dumps({"dataset_manifest": {"queries": []}, "result_profile": {"row_count": 0}})
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["action"] == "data_feedback"
    assert payload["impossible_reason"] == "tool_not_granted:python-sandbox:run_analysis_script"


def test_IV_falls_back_when_brain_partial_without_artifacts_step0(decision_ctx, monkeypatch):
    from data_analyst import service as mod

    monkeypatch.setattr(DataAnalystService, "_should_use_brain", staticmethod(lambda cfg: True))
    monkeypatch.setattr(
        DataAnalystService,
        "_run_brain",
        lambda self, **kwargs: {"action": "partial", "sandbox_steps": 0, "artifact_paths": []},
    )
    monkeypatch.setattr(
        mod,
        "analyze_datasets",
        lambda **kwargs: {"action": "complete", "artifact_paths": ["out/fallback.csv"]},
    )
    ctx = decision_ctx(
        goal=_goal(
            {
                "dataset_manifest": {"queries": [{"path": "/tmp/fake.parquet", "row_count": 3}]},
                "result_profile": {"row_count": 3},
            }
        )
    )
    payload = json.loads(_svc().decide(ctx).content)
    assert payload["action"] == "complete"
    assert payload["artifact_paths"] == ["out/fallback.csv"]
