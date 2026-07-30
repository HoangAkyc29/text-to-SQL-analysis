#!/usr/bin/env python3
"""Submit one analysis and poll until terminal (for UI/API regression gauntlet)."""

from __future__ import annotations

import json
import os
import sys
import time
import uuid

import httpx


def receptionist_answers(request: dict) -> dict:
    answers = []
    for question in request.get("questions") or []:
        qid = str(question.get("id") or "auto")
        options = question.get("options") or [{"id": "auto"}]
        answers.append({"question_id": qid, "selected_option_id": options[0]["id"]})
    return {"answers": answers}


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: _run_session.py <message> [session_label]", file=sys.stderr)
        return 2
    message = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else "session"
    base = os.getenv("CHAT_GATEWAY_URL", "http://127.0.0.1:18300").rstrip("/")
    pwd = os.getenv("AUTH_SEED_HQ_ANALYST_PASSWORD", "")
    if not pwd:
        print("missing AUTH_SEED_HQ_ANALYST_PASSWORD", file=sys.stderr)
        return 1
    session_id = f"{label}-{uuid.uuid4().hex[:8]}"
    with httpx.Client(timeout=120.0) as client:
        login = client.post(f"{base}/auth/login", json={"username": "hq.analyst", "password": pwd})
        login.raise_for_status()
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        client.post(
            f"{base}/sessions",
            headers=headers,
            json={"session_id": session_id, "title": message[:80]},
        )
        job = client.post(
            f"{base}/analyses",
            headers={**headers, "Idempotency-Key": uuid.uuid4().hex},
            json={"session_id": session_id, "message": message},
        )
        job.raise_for_status()
        body = job.json()
        analysis_id = body["analysis_id"]
        deadline = time.monotonic() + float(os.getenv("POLL_TIMEOUT", "1800"))
        answered: set[tuple[str, int]] = set()
        while time.monotonic() < deadline:
            st = client.get(f"{base}/analyses/{analysis_id}", headers=headers).json()
            status = str(st.get("status") or "")
            if status == "awaiting_interaction":
                iid = str(st.get("pending_interaction_id") or "")
                rev = int(st.get("revision") or 1)
                key = (iid, rev)
                if iid and key not in answered:
                    req = st.get("pending_interaction") or {}
                    client.post(
                        f"{base}/analyses/{analysis_id}/interactions",
                        headers=headers,
                        json={
                            "interaction_id": iid,
                            "expected_revision": rev,
                            "idempotency_key": f"{analysis_id}-{iid}-{rev}",
                            "response": receptionist_answers(req if isinstance(req, dict) else {}),
                        },
                    ).raise_for_status()
                    answered.add(key)
                time.sleep(2)
                continue
            if status in {"succeeded", "failed", "cancelled", "expired"}:
                out = {
                    "label": label,
                    "session_id": session_id,
                    "analysis_id": analysis_id,
                    "status": status,
                    "outcome": st.get("outcome"),
                    "trace_id": st.get("trace_id"),
                    "artifacts": len(st.get("artifacts") or []),
                    "error": st.get("error"),
                }
                print(json.dumps(out, ensure_ascii=False))
                return 0 if status == "succeeded" else 2
            time.sleep(8)
    print(json.dumps({"error": "timeout", "analysis_id": analysis_id}), file=sys.stderr)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
