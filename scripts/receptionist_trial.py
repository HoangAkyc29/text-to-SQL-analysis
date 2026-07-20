#!/usr/bin/env python3
"""Role-play receptionist trial: send initial question, answer clarifies, log all turns."""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.config.env import load_project_env  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

INITIAL_MESSAGE = (
    "Trong ngày 1/7/2026 tới ngày 6/7/2026, hãy xuất dữ liệu sau để tôi có thông tin về "
    "mặt hàng mã 0030344, 0030348 và 0030355. Đây là các mặt hàng quà tặng cho khách. "
    "Tôi cần biết số lượng mỗi quà tặng là bao nhiêu và kiểm tra tính hợp lệ của bill 600k trở lên. "
    "Sau đó xuất ra danh sách 5 bill gần nhất tương ứng với mỗi mặt hàng trên."
)

LOG_PATH = ROOT / "docs2" / "trial-receptionist-session.jsonl"


def receptionist_answers(clarification: dict[str, Any], analysis_id: str) -> dict[str, Any]:
    """Answer as non-technical receptionist; only explain 600k if explicitly asked."""
    answers: list[dict[str, Any]] = []
    for q in clarification.get("questions") or []:
        qid = q.get("id", "")
        prompt = (q.get("prompt") or "").lower()
        options = q.get("options") or []
        opt_id = options[0]["id"] if options else "unknown"
        other_text: str | None = None

        # Bill 600k validity — only explain when agent asks about it
        if any(k in prompt for k in ("600", "600k", "hợp lệ", "hop le", "giá trị bill", "gia tri")):
            other_text = (
                "Bill hợp lệ là bill có tổng giá trị từ 600.000 đồng trở lên. "
                "Nếu quà tặng nằm trong bill dưới 600k thì không tính vào thống kê."
            )
            for o in options:
                lbl = (o.get("label") or "").lower()
                if "600" in lbl or "tổng" in lbl or "tong" in lbl or "giá trị" in lbl:
                    opt_id = o["id"]
                    other_text = None
                    break
        elif any(k in prompt for k in ("bill", "hóa đơn", "hoa don", "giao dịch", "giao dich", "trans")):
            other_text = (
                "Tôi chỉ biết là mỗi lần khách mua sẽ có một bill — số bill in trên hóa đơn. "
                "Tôi không rành tên cột trong hệ thống, bạn tự tra giúp tôi nhé."
            )
            for o in options:
                if "trans" in (o.get("id") or "").lower() or "bill" in (o.get("label") or "").lower():
                    opt_id = o["id"]
                    other_text = None
                    break
        elif any(k in prompt for k in ("mã", "ma ", "sku", "item", "sản phẩm", "san pham", "plu")):
            other_text = (
                "Đúng rồi, đó là mã hàng tôi đưa — 0030344, 0030348, 0030355. "
                "Tôi không biết mã đó là 6 số hay 8 số trong máy, chỉ lấy trên phiếu quà."
            )
            # Prefer padded internal SKU when offered — gift PLUs are often 7 digits on the slip.
            for o in options:
                oid = (o.get("id") or "").lower()
                lbl = (o.get("label") or "").lower()
                if "sku_pad" in oid or "pad" in oid or "8 số" in lbl or "0 đầu" in lbl or "0 dau" in lbl:
                    opt_id = o["id"]
                    other_text = None
                    break
            else:
                for o in options:
                    lbl = (o.get("label") or "").lower()
                    if "item" in lbl or "plu" in lbl or "mã" in lbl or "sku" in lbl:
                        opt_id = o["id"]
                        other_text = None
                        break
        elif any(k in prompt for k in ("ngày", "ngay", "thời gian", "thoi gian", "date")):
            for o in options:
                lbl = (o.get("label") or "").lower()
                if "1/7" in lbl or "2026" in lbl or "range" in lbl:
                    opt_id = o["id"]
                    break
        elif any(k in prompt for k in ("số lượng", "so luong", "quantity", "đếm", "dem")):
            for o in options:
                lbl = (o.get("label") or "").lower()
                if "sum" in lbl or "count" in lbl or "tổng" in lbl or "số lượng" in lbl:
                    opt_id = o["id"]
                    break
        elif any(k in prompt for k in ("5 bill", "gần nhất", "gan nhat", "latest", "top")):
            for o in options:
                lbl = (o.get("label") or "").lower()
                if "5" in lbl or "top" in lbl or "gần" in lbl:
                    opt_id = o["id"]
                    break
        else:
            # Default: first option or exploration
            for o in options:
                if o.get("id") not in ("unknown", "explore"):
                    opt_id = o["id"]
                    break

        ans: dict[str, Any] = {"question_id": qid, "selected_option_id": opt_id}
        if other_text:
            ans["other_text"] = other_text
        answers.append(ans)

    return {"analysis_id": analysis_id, "answers": answers}


def append_log(record: dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> int:
    load_project_env(ROOT)
    base = os.getenv("CHAT_GATEWAY_URL", "http://localhost:18300").rstrip("/")
    password = os.getenv("AUTH_SEED_HQ_ANALYST_PASSWORD", "")
    if not password:
        print("missing AUTH_SEED_HQ_ANALYST_PASSWORD", file=sys.stderr)
        return 1

    session_id = f"receptionist-trial-{uuid.uuid4().hex[:8]}"
    if LOG_PATH.exists():
        LOG_PATH.unlink()

    # Must exceed pipeline.max_sync_seconds: a late Agent II call can still run
    # up to the gateway httpx timeout after the sync deadline check.
    with httpx.Client(timeout=1800.0) as client:
        login = client.post(
            f"{base}/auth/login",
            json={"username": "hq.analyst", "password": password},
        )
        if login.status_code != 200:
            print("login failed", login.text[:300])
            return 1
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        append_log({"ts": time.time(), "role": "user", "session_id": session_id, "message": INITIAL_MESSAGE})
        resp = client.post(
            f"{base}/chat",
            json={"session_id": session_id, "message": INITIAL_MESSAGE},
            headers=headers,
        )
        body = resp.json() if resp.status_code == 200 else {"error": resp.text}
        append_log({"ts": time.time(), "role": "system", "endpoint": "/chat", "status": resp.status_code, "body": body})
        print(json.dumps(body, ensure_ascii=False, indent=2))

        max_rounds = 8
        for round_i in range(max_rounds):
            wf = body.get("workflow_status")
            outcome = body.get("outcome")
            if wf not in ("awaiting_clarification",) and outcome != "needs_clarification":
                if body.get("error"):
                    print("ERROR:", body.get("error"))
                    return 1
                print("DONE workflow_status=", wf, "outcome=", outcome)
                break

            clarification = body.get("clarification")
            analysis_id = body.get("analysis_id") or ""
            if not clarification or not analysis_id:
                print("stuck: needs clarification but missing payload")
                return 1

            reply = receptionist_answers(clarification, analysis_id)
            append_log({"ts": time.time(), "role": "receptionist_reply", "reply": reply, "clarification": clarification})

            resp = client.post(
                f"{base}/chat/clarify",
                json={"session_id": session_id, "reply": reply},
                headers=headers,
            )
            body = resp.json() if resp.status_code == 200 else {"error": resp.text}
            append_log(
                {
                    "ts": time.time(),
                    "role": "system",
                    "endpoint": "/chat/clarify",
                    "round": round_i + 1,
                    "status": resp.status_code,
                    "body": body,
                }
            )
            print(f"\n--- clarify round {round_i + 1} ---")
            print(json.dumps({k: body.get(k) for k in ("outcome", "workflow_status", "message", "error")}, ensure_ascii=False))
        else:
            print("max clarify rounds exceeded")
            return 1

    print(f"\nSession log: {LOG_PATH}")
    print(f"session_id: {session_id}")
    print(f"analysis_id: {body.get('analysis_id')}")
    print(f"trace_id: {body.get('trace_id')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
