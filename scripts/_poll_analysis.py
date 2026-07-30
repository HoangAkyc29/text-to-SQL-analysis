#!/usr/bin/env python3
"""Poll analysis job until terminal; auto-answer clarifications (first option)."""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any

import httpx


def receptionist_answers(request: dict[str, Any]) -> dict[str, Any]:
    answers: list[dict[str, Any]] = []
    for question in request.get("questions") or []:
        qid = str(question.get("id") or "auto")
        options = question.get("options") or [{"id": "auto"}]
        answers.append({"question_id": qid, "selected_option_id": options[0]["id"]})
    return {"answers": answers}


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: poll_analysis.py <analysis_id>", file=sys.stderr)
        return 2
    analysis_id = sys.argv[1]
    base = os.getenv("CHAT_GATEWAY_INTERNAL_URL", "http://127.0.0.1:8000").rstrip("/")
    pwd = os.getenv("AUTH_SEED_HQ_ANALYST_PASSWORD", "")
    if not pwd:
        print("missing AUTH_SEED_HQ_ANALYST_PASSWORD", file=sys.stderr)
        return 1
    timeout = float(os.getenv("POLL_TIMEOUT", "1800"))
    with httpx.Client(timeout=60.0) as client:
        login = client.post(f"{base}/auth/login", json={"username": "hq.analyst", "password": pwd})
        login.raise_for_status()
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        answered: set[tuple[str, int]] = set()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            job = client.get(f"{base}/analyses/{analysis_id}", headers=headers).json()
            status = str(job.get("status") or "")
            summary = {
                "status": status,
                "outcome": job.get("outcome"),
                "trace_id": job.get("trace_id"),
                "pending": job.get("pending_interaction_id"),
                "artifacts": len(job.get("artifacts") or []),
            }
            print(json.dumps(summary, ensure_ascii=False), flush=True)
            if status == "awaiting_interaction":
                iid = str(job.get("pending_interaction_id") or "")
                rev = int(job.get("revision") or 1)
                key = (iid, rev)
                if iid and key not in answered:
                    req = job.get("pending_interaction") or {}
                    if not req.get("questions"):
                        # Pull latest interaction_requested event
                        with client.stream(
                            "GET",
                            f"{base}/analyses/{analysis_id}/events",
                            headers=headers,
                            timeout=30.0,
                        ) as resp:
                            for line in resp.iter_lines():
                                if not line.startswith(b"data:"):
                                    continue
                                try:
                                    data = json.loads(line[5:].strip())
                                except json.JSONDecodeError:
                                    continue
                                et = str(data.get("event_type") or data.get("type") or "")
                                if et == "interaction_requested":
                                    req = data.get("request") or req
                    payload = receptionist_answers(req if isinstance(req, dict) else {})
                    reply = client.post(
                        f"{base}/analyses/{analysis_id}/interactions",
                        headers=headers,
                        json={
                            "interaction_id": iid,
                            "expected_revision": rev,
                            "idempotency_key": f"{analysis_id}-{iid}-{rev}",
                            "response": payload,
                        },
                    )
                    print(
                        json.dumps(
                            {"interaction_reply": reply.status_code, "body": reply.text[:500]},
                            ensure_ascii=False,
                        ),
                        flush=True,
                    )
                    reply.raise_for_status()
                    answered.add(key)
                time.sleep(2)
                continue
            if status in {"succeeded", "failed", "cancelled", "expired"}:
                out_path = os.getenv("POLL_OUT")
                if out_path:
                    with open(out_path, "w", encoding="utf-8") as fh:
                        json.dump(job, fh, ensure_ascii=False, indent=2)
                print("FINAL", json.dumps(job, ensure_ascii=False), flush=True)
                return 0 if status == "succeeded" else 2
            time.sleep(5)
    print("timeout", file=sys.stderr)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
