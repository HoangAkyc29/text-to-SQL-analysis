#!/usr/bin/env python3
"""Export a live-trial evaluation bundle for one analysis_id.

Prefer the authenticated API (works while stack is up). Falls back to reading
JSONL from the chat-gateway/analysis-worker Docker volume when --from-volume.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.config.env import load_project_env  # noqa: E402


def _api_export(base_url: str, token: str, analysis_id: str) -> dict:
    import httpx

    url = f"{base_url.rstrip('/')}/analyses/{analysis_id}/trial-log"
    response = httpx.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=60.0,
    )
    response.raise_for_status()
    return response.json()


def _volume_jsonl(container: str, analysis_id: str) -> list[dict]:
    safe = "".join(ch for ch in analysis_id if ch.isalnum() or ch in "-_")
    remote = f"/app/data/state/live-trials/{safe}.jsonl"
    try:
        out = subprocess.check_output(
            ["docker", "exec", container, "cat", remote],
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    rows: list[dict] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"raw": line, "parse_error": True})
    return rows


def main() -> int:
    load_project_env()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis_id")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSON path (default: docs2/live_trials/<id>.json)",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("CHAT_GATEWAY_URL", "http://localhost:18300"),
    )
    parser.add_argument("--token", default=os.getenv("LIVE_TRIAL_TOKEN", ""))
    parser.add_argument(
        "--from-volume",
        action="store_true",
        help="Only dump JSONL from Docker volume (no Mongo bundle)",
    )
    parser.add_argument(
        "--container",
        default="monorepo-trading-agent-chat-gateway-1",
    )
    args = parser.parse_args()

    out = args.out or (ROOT / "docs2" / "live_trials" / f"{args.analysis_id}.json")
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.from_volume:
        bundle = {
            "analysis_id": args.analysis_id,
            "file_log": _volume_jsonl(args.container, args.analysis_id),
            "source": "docker_volume",
        }
    else:
        if not args.token:
            print(
                "Need --token or LIVE_TRIAL_TOKEN (login JWT). "
                "Or use --from-volume for JSONL-only.",
                file=sys.stderr,
            )
            return 2
        bundle = _api_export(args.base_url, args.token, args.analysis_id)

    out.write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"wrote {out} ({len(bundle.get('file_log') or bundle.get('events') or [])} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
