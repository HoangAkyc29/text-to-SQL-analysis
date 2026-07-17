"""Unit tests for Agent IV sandbox / reason_loop hardening."""

from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

from project_core.domain.contracts.workflow import PermissionsSnapshot


def _perms() -> PermissionsSnapshot:
    return PermissionsSnapshot(
        actor_id="user-1",
        role="hq_analyst",
        allowed_tables=["STRANS"],
        tool_grants=["tool:python-sandbox:run_analysis_script"],
    )


def test_runner_child_allows_common_builtins(tmp_path, monkeypatch):
    from python_sandbox import runner_child

    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    monkeypatch.setenv("ARTIFACTS_DIR", str(artifacts))
    monkeypatch.setenv("ATTACHMENTS_DIR", str(tmp_path / "attachments"))

    import pandas as pd

    dataset = artifacts / "raw" / "q.parquet"
    dataset.parent.mkdir(parents=True)
    pd.DataFrame({"sku": ["a", "b"], "qty": [1, 2]}).to_parquet(dataset)

    out = artifacts / "out" / "step"
    out.mkdir(parents=True)
    script = (
        "df = pd.read_parquet(path)\n"
        "cols = list(df.columns)\n"
        "total = sum(df['qty'])\n"
        "rows = [{'i': i, 'c': c} for i, c in enumerate(sorted(cols))]\n"
        "pd.DataFrame(rows).to_csv(out / 'ok.csv', index=False)\n"
        "pd.DataFrame([{'total': total}]).to_csv(out / 'tot.csv', index=False)\n"
    )

    old_stdin, old_argv, old_stdout = sys.stdin, sys.argv, sys.stdout
    buf = StringIO()
    try:
        sys.stdin = StringIO(script)
        sys.argv = ["runner_child.py", str(dataset), str(out)]
        sys.stdout = buf
        code = runner_child.main()
    finally:
        sys.stdin, sys.argv, sys.stdout = old_stdin, old_argv, old_stdout

    assert code == 0
    payload = json.loads(buf.getvalue().strip())
    assert payload["status"] == "ok"
    assert (out / "ok.csv").exists()
    assert (out / "tot.csv").exists()


def test_iv_brain_observation_includes_script_detail(monkeypatch):
    from project_core.domain.access.context_policy import ContextPolicy
    from project_core.domain.analysis import iv_brain
    from project_core.domain.contracts.brief import AnalysisBrief

    class FakeSandbox:
        def run_analysis_script(self, path, script, output_dir, tool_grants=None):
            return {"error": "script_failed", "detail": "name 'list' is not defined"}

    class FakePlanner:
        def __init__(self, *a, **k):
            self.tokens = 3
            self._n = 0

        def next_decision(self, state):
            self._n += 1
            if self._n == 1:
                return {
                    "decision": "run_step",
                    "thought": "aggregate",
                    "step": {"kind": "script", "dataset_index": 0, "script": "x=list()"},
                }
            return {
                "decision": "finalize",
                "status": "partial",
                "insight_vi": "partial because script failed",
                "headline_metrics": {},
                "caveats": [],
            }

    monkeypatch.setattr(iv_brain, "_sandbox", lambda: FakeSandbox())
    monkeypatch.setattr(iv_brain, "AnalysisPlanner", FakePlanner)
    monkeypatch.setattr(
        iv_brain.DataProfiler,
        "profile",
        lambda self, paths, meta: [
            {
                "index": 0,
                "role": "main",
                "path": "/tmp/fake.parquet",
                "columns": ["sku"],
                "row_count": 2,
                "sample": [],
            }
        ],
    )
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "mkdir", lambda self, parents=False, exist_ok=False: None)

    brief = AnalysisBrief(intent="test", metrics=["qty"])
    payload = iv_brain.run_analysis_brain(
        brief=brief,
        manifest={"queries": [{"path": "/tmp/fake.parquet", "row_count": 2}]},
        profile={"row_count": 2, "columns": ["sku", "qty"]},
        out_dir="/tmp/out",
        max_steps=4,
        query_meta=[{"role": "main", "purpose": "agg"}],
        recipe_candidates=[],
        domain_rules_excerpt="",
        permissions=_perms(),
        context_policy=ContextPolicy(),
        llm=object(),
        profile_name="analyst",
        system_prompt="x",
    )
    assert payload["action"] == "partial"
    assert payload["sandbox_steps"] == 1
    assert any("list" in c for c in payload["caveats"])
    assert payload["steps_trace"][0]["error"] and "list" in payload["steps_trace"][0]["error"]


def test_iv_brain_marks_empty_ok_script_as_no_files_written(monkeypatch):
    from project_core.domain.access.context_policy import ContextPolicy
    from project_core.domain.analysis import iv_brain
    from project_core.domain.contracts.brief import AnalysisBrief

    class FakeSandbox:
        def run_analysis_script(self, path, script, output_dir, tool_grants=None):
            return {"status": "ok", "artifacts": []}

    class FakePlanner:
        def __init__(self, *a, **k):
            self.tokens = 1
            self._n = 0

        def next_decision(self, state):
            self._n += 1
            if self._n == 1:
                return {
                    "decision": "run_step",
                    "step": {
                        "kind": "script",
                        "dataset_index": 0,
                        "script": "df=pd.read_parquet(path)",
                    },
                }
            return {"decision": "finalize", "status": "partial", "insight_vi": "done"}

    monkeypatch.setattr(iv_brain, "_sandbox", lambda: FakeSandbox())
    monkeypatch.setattr(iv_brain, "AnalysisPlanner", FakePlanner)
    monkeypatch.setattr(
        iv_brain.DataProfiler,
        "profile",
        lambda self, paths, meta: [
            {"index": 0, "role": "main", "columns": ["a"], "row_count": 1, "sample": []}
        ],
    )
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "mkdir", lambda self, parents=False, exist_ok=False: None)

    brief = AnalysisBrief(intent="test", metrics=["a"])
    payload = iv_brain.run_analysis_brain(
        brief=brief,
        manifest={"queries": [{"path": "/tmp/x.parquet", "row_count": 1}]},
        profile={"row_count": 1},
        out_dir="/tmp/out",
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
    assert payload["sandbox_steps"] == 1
    assert any("no_files_written" in c for c in payload["caveats"])
