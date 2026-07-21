"""Unit tests for Agent IV op-based brain (no sandbox scripts)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from project_core.domain.contracts.workflow import PermissionsSnapshot


def _perms() -> PermissionsSnapshot:
    return PermissionsSnapshot(
        actor_id="user-1",
        role="hq_analyst",
        allowed_tables=["STRANS"],
        tool_grants=["tool:*"],
    )


def test_iv_brain_run_op_exports(tmp_path, monkeypatch):
    from project_core.domain.access.context_policy import ContextPolicy
    from project_core.domain.analysis import iv_brain
    from project_core.domain.contracts.brief import AnalysisBrief

    df = pd.DataFrame({"sku": ["a", "b"], "qty": [1, 2]})
    raw = tmp_path / "raw"
    raw.mkdir()
    path = raw / "q0.parquet"
    df.to_parquet(path, index=False)
    out = tmp_path / "out"
    out.mkdir()

    class FakePlanner:
        def __init__(self, *a, **k):
            self.tokens = 2
            self._n = 0

        def next_decision(self, state):
            self._n += 1
            if self._n == 1:
                return {
                    "decision": "run_op",
                    "thought": "export",
                    "op": {
                        "op_id": "export_csv",
                        "dataset": "q0",
                        "args": {"filename": "summary.csv"},
                    },
                }
            return {
                "decision": "finalize",
                "status": "complete",
                "insight_vi": "ok",
                "headline_metrics": {"qty": 3},
            }

    monkeypatch.setattr(iv_brain, "AnalysisPlanner", FakePlanner)

    payload = iv_brain.run_analysis_brain(
        brief=AnalysisBrief(intent="test", metrics=["qty"], output_format=["table"]),
        manifest={"queries": [{"path": str(path), "row_count": 2}]},
        profile={"row_count": 2},
        out_dir=str(out),
        max_steps=4,
        query_meta=[{"role": "main"}],
        recipe_candidates=[],
        domain_rules_excerpt="",
        permissions=_perms(),
        context_policy=ContextPolicy(),
        llm=object(),
        profile_name="analyst",
        system_prompt="x",
    )
    assert payload["action"] == "complete"
    assert payload["artifact_paths"]
    assert Path(payload["artifact_paths"][0]).exists()


def test_iv_brain_rejects_script(tmp_path, monkeypatch):
    from project_core.domain.access.context_policy import ContextPolicy
    from project_core.domain.analysis import iv_brain
    from project_core.domain.contracts.brief import AnalysisBrief

    df = pd.DataFrame({"a": [1]})
    path = tmp_path / "q.parquet"
    df.to_parquet(path, index=False)
    out = tmp_path / "out"
    out.mkdir()

    class FakePlanner:
        def __init__(self, *a, **k):
            self.tokens = 1
            self._n = 0

        def next_decision(self, state):
            self._n += 1
            if self._n == 1:
                return {
                    "decision": "run_step",
                    "step": {"kind": "script", "script": "x=1"},
                }
            return {
                "decision": "finalize",
                "status": "partial",
                "insight_vi": "done",
            }

    monkeypatch.setattr(iv_brain, "AnalysisPlanner", FakePlanner)
    payload = iv_brain.run_analysis_brain(
        brief=AnalysisBrief(intent="test", metrics=["a"]),
        manifest={"queries": [{"path": str(path), "row_count": 1}]},
        profile={"row_count": 1},
        out_dir=str(out),
        max_steps=3,
        query_meta=[{"role": "main"}],
        recipe_candidates=[],
        domain_rules_excerpt="",
        permissions=_perms(),
        context_policy=ContextPolicy(),
        llm=object(),
        profile_name="analyst",
        system_prompt="x",
    )
    # Script rejected; finalize may auto-export CSV so action can be partial.
    assert any(
        "script_ops_disabled" in str(c)
        for c in (payload.get("caveats") or [])
    ) or any(
        "script_ops_disabled" in str(s.get("error") or "")
        for s in (payload.get("steps_trace") or [])
    )
    assert payload["action"] in {"data_feedback", "partial", "complete"}
    if payload["action"] == "data_feedback":
        assert payload.get("data_feedback")
    else:
        assert payload.get("artifact_paths"), "auto-export should produce artifacts after script reject"


def test_analysis_planner_logs_preview_on_invalid_json(caplog):
    from project_core.domain.analysis.iv_brain import AnalysisPlanner

    class FakeResult:
        content = ""
        usage_tokens = 0

    class FakeLLM:
        def chat(self, **kwargs):
            return FakeResult()

    planner = AnalysisPlanner(FakeLLM(), "analyst", "system")
    with caplog.at_level("WARNING"):
        with pytest.raises(json.JSONDecodeError):
            planner.next_decision({"x": 1})
    assert "invalid JSON content preview" in caplog.text
