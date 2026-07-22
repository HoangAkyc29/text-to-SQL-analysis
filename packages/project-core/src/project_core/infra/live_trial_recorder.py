"""Durable live-trial logging for human-in-the-loop evaluation."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from project_core.infra.analysis_repository import sanitize_public_data


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class LiveTrialRecorder:
    """Append-only JSONL mirror next to Mongo analysis_events.

    Files land under ``data/state/live-trials/`` (Docker volume) so human trials
    remain inspectable after container restarts.
    """

    def __init__(self, base_dir: str | Path | None = None) -> None:
        root = Path(
            base_dir
            or os.getenv("LIVE_TRIAL_LOG_DIR")
            or Path(os.getenv("AGENT_DATA_DIR", "data")) / "state" / "live-trials"
        )
        self.base_dir = root
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, analysis_id: str) -> Path:
        safe = "".join(ch for ch in analysis_id if ch.isalnum() or ch in "-_")
        return self.base_dir / f"{safe}.jsonl"

    def append(
        self,
        analysis_id: str,
        event_type: str,
        data: dict[str, Any] | None = None,
        *,
        source: str = "system",
    ) -> dict[str, Any]:
        record = {
            "ts": utc_now_iso(),
            "analysis_id": analysis_id,
            "event_type": event_type,
            "source": source,
            "data": sanitize_public_data(data or {}),
        }
        path = self.path_for(analysis_id)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        return record

    def read(self, analysis_id: str) -> list[dict[str, Any]]:
        path = self.path_for(analysis_id)
        if not path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({"raw": line, "parse_error": True})
        return rows


def export_trial_bundle(
    *,
    analysis_id: str,
    repository: Any,
    actor_id: str,
    recorder: LiveTrialRecorder | None = None,
    audit_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build an evaluation bundle from Mongo + JSONL + optional audit excerpts."""
    recorder = recorder or LiveTrialRecorder()
    job = repository.get_job(analysis_id, actor_id)
    if job is None:
        raise KeyError(analysis_id)
    events = [
        event.model_dump(mode="json")
        for event in repository.list_events(analysis_id, after=0, limit=5000)
    ]
    interactions = [
        item.model_dump(mode="json")
        for item in repository.list_interactions(analysis_id, actor_id)
    ]
    artifacts = [
        item.model_dump(mode="json")
        for item in repository.list_artifacts(analysis_id, actor_id)
    ]
    transcript = [
        item.model_dump(mode="json")
        for item in repository.list_transcript(job.session_id, actor_id)
    ]
    file_log = recorder.read(analysis_id)
    audit_hits: list[dict[str, Any]] = []
    legacy_id = job.legacy_analysis_id
    path = Path(
        audit_path
        or os.getenv("SQL_AUDIT_LOG_PATH")
        or Path(os.getenv("AGENT_DATA_DIR", "data")) / "state" / "audit.jsonl"
    )
    if path.exists() and legacy_id:
        for line in path.read_text(encoding="utf-8").splitlines():
            if legacy_id not in line and analysis_id not in line:
                continue
            try:
                audit_hits.append(sanitize_public_data(json.loads(line)))
            except json.JSONDecodeError:
                continue
    return {
        "exported_at": utc_now_iso(),
        "analysis_id": analysis_id,
        "job": job.model_dump(mode="json"),
        "events": events,
        "file_log": file_log,
        "interactions": interactions,
        "artifacts": artifacts,
        "transcript": transcript,
        "audit_excerpts": audit_hits,
    }
