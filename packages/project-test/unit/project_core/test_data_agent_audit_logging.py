"""Audit logger helpers for Data Agent / Tool-Selector."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from project_core.domain.audit.logger import AuditLogger, safe_args_preview
from project_core.infra.live_trial_recorder import export_trial_bundle


def test_safe_args_preview_redacts_sql_and_truncates_lists():
    preview = safe_args_preview(
        {
            "table": "TRANSHDR",
            "raw_sql": "SELECT 1",
            "filters": [{"column": "AMOUNT", "op": "gte", "value": 600000}],
            "sku_ids": [str(i) for i in range(20)],
        }
    )
    assert preview["raw_sql"] == "<redacted>"
    assert preview["table"] == "TRANSHDR"
    assert preview["sku_ids"]["len"] == 20
    assert len(preview["sku_ids"]["sample"]) <= 8


def test_log_data_agent_turn_and_selector_persist(tmp_path, monkeypatch):
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("SQL_AUDIT_LOG_PATH", str(audit_path))
    audit = AuditLogger()
    audit.log_data_agent_turn(
        trace_id="trace-abc",
        actor_id="actor-1",
        analysis_id="analysis-xyz",
        turn=2,
        phase="execute",
        decision="fetch",
        tool_id="query_rows",
        server="data-query",
        ok=True,
        row_count=10,
        save_as="sale_lines",
        args_preview={"table": "STRANS", "limit": 5000},
        chunk_goal="Fetch sale lines",
        selector_tool_ids=["query_rows"],
    )
    audit.log_tool_selector_suggest(
        trace_id="trace-abc",
        actor_id="actor-1",
        analysis_id="analysis-xyz",
        chunk_goal="Fetch sale lines",
        tools=[{"server": "data-query", "tool_id": "query_rows", "reason": "test"}],
        turn=2,
    )
    audit.log_data_agent_summary(
        trace_id="trace-abc",
        actor_id="actor-1",
        analysis_id="analysis-xyz",
        action="partial",
        duration_ms=12,
        stages=[{"stage_id": "t1", "goal": "x"}],
        tool_chain=[{"kind": "fetch", "tool_id": "query_rows", "args": {"table": "STRANS"}}],
        coverage={"ok": False, "gaps": ["top_n_mismatch:got_10_want_<=5"], "row_count": 10, "top_n": 5},
    )
    lines = [json.loads(x) for x in audit_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    types = [e["event_type"] for e in lines]
    assert "data_agent_turn" in types
    assert "tool_selector_suggest" in types
    assert "data_agent_summary" in types
    summary = next(e for e in lines if e["event_type"] == "data_agent_summary")
    assert summary["payload"]["analysis_id"] == "analysis-xyz"
    assert summary["payload"]["coverage"]["gaps"]


def test_export_trial_bundle_matches_trace_id(tmp_path, monkeypatch):
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("SQL_AUDIT_LOG_PATH", str(audit_path))
    audit = AuditLogger()
    audit.log_data_agent_summary(
        trace_id="trace-match-me",
        actor_id="a",
        analysis_id="analysis-1",
        action="partial",
        duration_ms=1,
        caveats=["top_n_mismatch:got_10_want_<=5"],
    )

    class _Repo:
        def get_job(self, analysis_id: str, actor_id: str):
            return SimpleNamespace(
                analysis_id=analysis_id,
                actor_id=actor_id,
                session_id="s1",
                legacy_analysis_id=None,
                trace_id="trace-match-me",
                model_dump=lambda mode="json": {
                    "analysis_id": analysis_id,
                    "trace_id": "trace-match-me",
                    "legacy_analysis_id": None,
                    "session_id": "s1",
                },
            )

        def list_events(self, *a, **k):
            return []

        def list_interactions(self, *a, **k):
            return []

        def list_artifacts(self, *a, **k):
            return []

        def list_transcript(self, *a, **k):
            return []

    bundle = export_trial_bundle(
        analysis_id="analysis-1",
        repository=_Repo(),
        actor_id="a",
        recorder=type("R", (), {"read": lambda self, _: []})(),
        audit_path=audit_path,
    )
    assert bundle["audit_excerpts"]
    assert any(e.get("event_type") == "data_agent_summary" for e in bundle["audit_excerpts"])
