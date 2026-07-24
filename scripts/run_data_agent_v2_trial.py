"""Run gift/30325 Data Agent trial against local chat-gateway. Writes summary only (no tokens)."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "http://localhost:18300"
OUT = Path("/tmp/trial_data_agent_v2_summary.json")
HOST_OUT_HINT = "data/artifacts/_trial_data_agent_v2_summary.json"
PROMPT = (
    "Trong ngày 1/7/2026 tới ngày 6/7/2026, với mặt hàng mã 30325 dạng quà tặng, "
    "cho tôi số lượng và các bill có giá trị từ 600000 trở lên, lấy 5 bill gần nhất."
)


def _refuse_if_stub_enabled() -> None:
    """Hard ban: never run product trials against ALLOW_LLM_STUB."""
    import os
    import urllib.error

    # Prefer live worker env via gateway health is insufficient; check via docker is caller duty.
    # Also refuse if this process itself has stub on.
    if os.getenv("ALLOW_LLM_STUB", "").strip().lower() in {"1", "true", "yes", "on"}:
        raise SystemExit("REFUSED: ALLOW_LLM_STUB is set — live LLM trial only")


def _json(method: str, path: str, body: dict | None = None, token: str | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} -> {exc.code}: {detail}") from exc


def main() -> None:
    _refuse_if_stub_enabled()
    # Also refuse if the running analysis-worker still has stub enabled.
    import subprocess

    try:
        env = subprocess.check_output(
            ["docker", "compose", "exec", "-T", "analysis-worker", "printenv", "ALLOW_LLM_STUB"],
            cwd=str(Path(__file__).resolve().parents[1]),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        env = ""
    if env.lower() in {"1", "true", "yes", "on"}:
        raise SystemExit(
            f"REFUSED: analysis-worker ALLOW_LLM_STUB={env!r} — recreate with ALLOW_LLM_STUB=0"
        )
    login = _json(
        "POST",
        "/auth/dev-login",
        {"actor_id": "22222222-2222-2222-2222-222222222222", "role": "hq_analyst"},
    )
    token = login["access_token"]
    session_id = f"trial-da-v2-{uuid.uuid4().hex[:12]}"
    _json(
        "POST",
        "/sessions",
        {"session_id": session_id, "title": "Data Agent v2 trial 30325"},
        token=token,
    )
    submitted = _json(
        "POST",
        "/analyses",
        {"session_id": session_id, "message": PROMPT},
        token=token,
    )
    analysis_id = submitted["analysis_id"]
    status = submitted.get("status")
    deadline = time.time() + 600
    job: dict = submitted
    while time.time() < deadline:
        job = _json("GET", f"/analyses/{analysis_id}", token=token)
        status = str(job.get("status") or "").lower()
        if status in {
            "succeeded",
            "failed",
            "cancelled",
            "expired",
            "awaiting_interaction",
        }:
            break
        time.sleep(3)

    # trial-log if available
    trial_log = None
    try:
        trial_log = _json("GET", f"/analyses/{analysis_id}/trial-log", token=token)
    except Exception as exc:  # noqa: BLE001
        trial_log = {"error": str(exc)}

    artifacts = job.get("artifacts") or []
    summary = {
        "session_id": session_id,
        "analysis_id": analysis_id,
        "status": job.get("status"),
        "outcome": job.get("outcome") or job.get("result_outcome"),
        "message_preview": (job.get("result_message") or job.get("message") or "")[:500],
        "artifact_count": len(artifacts),
        "artifact_names": [a.get("file_name") or a.get("name") for a in artifacts][:20],
        "pending_interaction": bool(job.get("pending_interaction")),
        "error": job.get("error"),
        "trial_log_keys": list(trial_log.keys()) if isinstance(trial_log, dict) else None,
        "trial_log_excerpt": _excerpt_trial(trial_log),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def _excerpt_trial(trial_log: dict | None) -> dict:
    if not isinstance(trial_log, dict):
        return {}
    steps = trial_log.get("steps") or trial_log.get("workflow_steps") or []
    texts = []
    for s in steps[:40]:
        if isinstance(s, dict):
            texts.append(
                {
                    "type": s.get("step_type") or s.get("type"),
                    "summary": str(s.get("summary") or "")[:200],
                }
            )
    # Look for data_agent markers in raw blob
    blob = json.dumps(trial_log, ensure_ascii=False)
    return {
        "has_plan_sql": "plan_sql" in blob.lower(),
        "has_data_agent": "data_agent" in blob.lower() or "fetches=" in blob,
        "has_resolve_products": "resolve_products" in blob,
        "has_trans_code_113": "TRANS_CODE" in blob and "'113'" in blob,
        "step_summaries": texts[:15],
        "keys": sorted(trial_log.keys())[:30],
    }


if __name__ == "__main__":
    try:
        main()
    except (URLError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        raise SystemExit(1) from exc
