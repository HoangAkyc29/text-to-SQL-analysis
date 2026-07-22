#!/usr/bin/env python3
"""Interactive live-trial harness against durable REST + SSE analysis APIs."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.config.env import load_project_env  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


DEFAULT_MESSAGE = (
    "Trong ngày 1/7/2026 tới ngày 6/7/2026, hãy xuất dữ liệu sau để tôi có thông tin về "
    "mặt hàng mã 0030344, 0030348 và 0030355. Đây là các mặt hàng quà tặng cho khách. "
    "Tôi cần biết số lượng mỗi quà tặng là bao nhiêu và kiểm tra tính hợp lệ của bill 600k trở lên. "
    "Sau đó xuất ra danh sách 5 bill gần nhất tương ứng với mỗi mặt hàng trên."
)


def receptionist_answers(request: dict[str, Any]) -> dict[str, Any]:
    answers: list[dict[str, Any]] = []
    for question in request.get("questions") or []:
        qid = str(question.get("id") or "")
        prompt = str(question.get("prompt") or "").lower()
        options = question.get("options") or []
        selected = options[0]["id"] if options else "unknown"
        other_text: str | None = None
        if any(token in prompt for token in ("600", "hợp lệ", "hop le", "giá trị bill")):
            other_text = (
                "Bill hợp lệ là bill có tổng giá trị từ 600.000 đồng trở lên. "
                "Nếu quà tặng nằm trong bill dưới 600k thì không tính vào thống kê."
            )
            for option in options:
                label = str(option.get("label") or "").lower()
                if "600" in label or "tổng" in label or "giá trị" in label:
                    selected = option["id"]
                    other_text = None
                    break
        answer: dict[str, Any] = {
            "question_id": qid,
            "selected_option_id": selected,
        }
        if other_text:
            answer["other_text"] = other_text
            answer["evidence"] = other_text
        answers.append(answer)
    return {"answers": answers}


def consume_sse(
    client: httpx.Client,
    url: str,
    headers: dict[str, str],
    *,
    last_event_id: str | None,
    timeout_s: float,
) -> tuple[list[dict[str, Any]], str | None, bool]:
    request_headers = dict(headers)
    if last_event_id:
        request_headers["Last-Event-ID"] = last_event_id
    events: list[dict[str, Any]] = []
    terminal = False
    current_id = last_event_id
    with client.stream("GET", url, headers=request_headers, timeout=timeout_s) as response:
        response.raise_for_status()
        event_name = "message"
        data_lines: list[str] = []
        for raw_line in response.iter_lines():
            line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else str(raw_line)
            if line == "":
                if not data_lines:
                    event_name = "message"
                    continue
                payload = "\n".join(data_lines)
                data_lines = []
                if event_name == "heartbeat":
                    event_name = "message"
                    continue
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    data = {"raw": payload}
                events.append({"id": current_id, "event": event_name, "data": data})
                event_type = str(
                    data.get("event_type")
                    or data.get("type")
                    or event_name
                )
                if event_type in {"completed", "failed", "cancelled", "interaction_requested"}:
                    terminal = True
                    break
                event_name = "message"
                continue
            if line.startswith(":"):
                continue
            if line.startswith("id:"):
                current_id = line[3:].strip()
            elif line.startswith("event:"):
                event_name = line[6:].strip() or "message"
            elif line.startswith("data:"):
                data_lines.append(line[5:].lstrip())
    return events, current_id, terminal


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", default=DEFAULT_MESSAGE)
    parser.add_argument("--timeout", type=float, default=1800.0)
    parser.add_argument(
        "--persona",
        choices=("auto", "human"),
        default="auto",
        help="auto answers clarifications; human pauses for stdin.",
    )
    args = parser.parse_args()
    load_project_env(ROOT)

    base = os.getenv("CHAT_GATEWAY_URL", "http://localhost:18300").rstrip("/")
    password = os.getenv("AUTH_SEED_HQ_ANALYST_PASSWORD", "")
    if not password:
        print("missing AUTH_SEED_HQ_ANALYST_PASSWORD", file=sys.stderr)
        return 1

    session_id = f"interactive-trial-{uuid.uuid4().hex[:8]}"
    log_path = ROOT / "docs2" / f"{session_id}.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(record: dict[str, Any]) -> None:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    with httpx.Client(timeout=args.timeout) as client:
        login = client.post(
            urljoin(base + "/", "auth/login"),
            json={"username": "hq.analyst", "password": password},
        )
        login.raise_for_status()
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        session = client.post(
            urljoin(base + "/", "sessions"),
            headers=headers,
            json={"session_id": session_id, "title": "Interactive live trial"},
        )
        if session.status_code not in {200, 201}:
            print("session create failed", session.text[:400], file=sys.stderr)
            return 1

        submit = client.post(
            urljoin(base + "/", "analyses"),
            headers={**headers, "Idempotency-Key": f"trial-{session_id}"},
            json={"session_id": session_id, "message": args.message},
        )
        if submit.status_code not in {200, 202}:
            print("analysis submit failed", submit.text[:400], file=sys.stderr)
            return 1
        job = submit.json()
        analysis_id = job.get("analysis_id") or job.get("id")
        log({"ts": time.time(), "role": "submit", "body": job})
        print(json.dumps(job, ensure_ascii=False, indent=2))
        if not analysis_id:
            print("missing analysis_id", file=sys.stderr)
            return 1

        events_url = urljoin(base + "/", f"analyses/{analysis_id}/events")
        last_event_id: str | None = None
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            batch, last_event_id, terminal = consume_sse(
                client,
                events_url,
                headers,
                last_event_id=last_event_id,
                timeout_s=min(60.0, max(5.0, deadline - time.monotonic())),
            )
            for event in batch:
                log({"ts": time.time(), "role": "event", "event": event})
                print(json.dumps(event, ensure_ascii=False))
                data = event.get("data") or {}
                event_type = str(data.get("event_type") or data.get("type") or "")
                if event_type == "interaction_requested":
                    interaction_id = data.get("interaction_id")
                    revision = int(data.get("revision") or 1)
                    request = (data.get("request") or {}) if isinstance(data, dict) else {}
                    if args.persona == "human":
                        print("Awaiting human interaction response on stdin as JSON...")
                        response_payload = json.loads(sys.stdin.readline())
                    else:
                        response_payload = receptionist_answers(request)
                    answer = client.post(
                        urljoin(base + "/", f"analyses/{analysis_id}/interactions"),
                        headers=headers,
                        json={
                            "interaction_id": interaction_id,
                            "expected_revision": revision,
                            "idempotency_key": f"{analysis_id}-{interaction_id}-{revision}",
                            "response": response_payload,
                        },
                    )
                    log(
                        {
                            "ts": time.time(),
                            "role": "interaction_reply",
                            "status": answer.status_code,
                            "body": answer.json() if answer.headers.get("content-type", "").startswith("application/json") else answer.text,
                        }
                    )
                    answer.raise_for_status()
                if event_type in {"completed", "failed", "cancelled"}:
                    status = client.get(
                        urljoin(base + "/", f"analyses/{analysis_id}"),
                        headers=headers,
                    )
                    print("FINAL", json.dumps(status.json(), ensure_ascii=False, indent=2))
                    log({"ts": time.time(), "role": "final", "body": status.json()})
                    print(f"Session log: {log_path}")
                    return 0 if event_type == "completed" else 2
            if terminal:
                continue
        print("timeout waiting for terminal analysis event", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
