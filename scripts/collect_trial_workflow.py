#!/usr/bin/env python3
"""Collect full workflow evidence for a trial session/trace."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.config.env import load_project_env  # noqa: E402
from project_core.infra.stm.redis_store import RedisSessionStore  # noqa: E402


def _read_audit(trace_id: str | None) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for rel in ("data/state/audit.jsonl",):
        p = ROOT / rel
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if trace_id is None or ev.get("trace_id") == trace_id:
                events.append(ev)
    return events


def _docker_audit(trace_id: str | None) -> list[dict[str, Any]]:
    try:
        out = subprocess.check_output(
            ["docker", "exec", "monorepo-trading-agent-chat-gateway-1", "cat", "/app/data/state/audit.jsonl"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    events = []
    for line in out.splitlines():
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if trace_id is None or ev.get("trace_id") == trace_id:
            events.append(ev)
    return events


def _mongo_snapshots(trace_id: str | None) -> dict[str, Any]:
    try:
        from pymongo import MongoClient
    except ImportError:
        return {}
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:18217/supermarket_agent")
    client = MongoClient(uri)
    db = client.get_default_database()
    out: dict[str, Any] = {"counts": {}}
    for coll in ("case_studies", "analysis_tools", "domain_rules", "schema_chunks"):
        if coll in db.list_collection_names():
            out["counts"][coll] = db[coll].count_documents({})
            if trace_id and coll == "case_studies":
                doc = db[coll].find_one({"source_trace_id": trace_id})
                if doc:
                    doc.pop("embedding", None)
                    out["case_for_trace"] = doc
    return out


def _artifacts(trace_id: str | None) -> dict[str, Any]:
    if not trace_id:
        return {}
    base = ROOT / "data" / "artifacts" / trace_id
    docker_base = Path(f"/app/data/artifacts/{trace_id}")
    info: dict[str, Any] = {"host_path": str(base), "files": []}
    search = base if base.exists() else None
    if search is None:
        try:
            listing = subprocess.check_output(
                [
                    "docker",
                    "exec",
                    "monorepo-trading-agent-chat-gateway-1",
                    "find",
                    f"/app/data/artifacts/{trace_id}",
                    "-type",
                    "f",
                ],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            info["docker_files"] = [x for x in listing.splitlines() if x.strip()]
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return info
    for f in search.rglob("*"):
        if f.is_file():
            info["files"].append({"path": str(f.relative_to(base)), "size": f.stat().st_size})
    return info


def main() -> int:
    load_project_env(ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-id", required=True)
    ap.add_argument("--trace-id", default="")
    ap.add_argument("--analysis-id", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    store = RedisSessionStore()
    bundle = store.load_session(args.session_id)
    workflow = bundle.workflow.model_dump(mode="json") if bundle.workflow else None
    transcript = [t.model_dump() for t in bundle.transcript]

    trace_id = args.trace_id or (bundle.workflow.last_completed_trace_id if bundle.workflow else "")
    audit = _read_audit(trace_id or None) or _docker_audit(trace_id or None)

    payload = {
        "session_id": args.session_id,
        "trace_id": trace_id,
        "analysis_id": args.analysis_id or (bundle.workflow.active_analysis_id if bundle.workflow else ""),
        "transcript": transcript,
        "workflow": workflow,
        "audit_events": audit,
        "mongo": _mongo_snapshots(trace_id or None),
        "artifacts": _artifacts(trace_id or None),
        "session_log": _read_jsonl(ROOT / "docs2" / "trial-receptionist-session.jsonl"),
    }

    out_path = Path(args.out) if args.out else ROOT / "docs2" / f"trial-workflow-raw-{args.session_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(out_path))
    return 0


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


if __name__ == "__main__":
    raise SystemExit(main())
