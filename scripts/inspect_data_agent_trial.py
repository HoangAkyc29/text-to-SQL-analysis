"""Inspect a trial analysis for Data Agent diagnostics."""

from __future__ import annotations

import json
import sys
from urllib.request import Request, urlopen

BASE = "http://localhost:18300"
AID = sys.argv[1] if len(sys.argv) > 1 else "2b0fa8f2-aee0-456a-a922-c617f999dcba"


def _json(method: str, path: str, body: dict | None = None, token: str | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    with urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    token = _json(
        "POST",
        "/auth/dev-login",
        {"actor_id": "22222222-2222-2222-2222-222222222222", "role": "hq_analyst"},
    )["access_token"]
    tl = _json("GET", f"/analyses/{AID}/trial-log", token=token)
    job = tl.get("job") or {}
    out = {
        "status": job.get("status"),
        "outcome": job.get("outcome"),
        "result_message": (job.get("result_message") or "")[:500],
        "technical_summary": job.get("technical_summary")
        or (job.get("result") or {}).get("technical_summary")
        if isinstance(job.get("result"), dict)
        else job.get("technical_summary"),
        "events_tail": [],
        "file_log_tail": [],
        "audit_tail": [],
        "blob_flags": {},
    }
    for ev in (tl.get("events") or [])[-25:]:
        out["events_tail"].append(
            {
                "type": ev.get("event_type") or ev.get("type"),
                "preview": str(ev.get("payload") or ev)[:350],
            }
        )
    fl = tl.get("file_log")
    if isinstance(fl, list):
        out["file_log_tail"] = [str(x)[:400] for x in fl[-40:]]
    elif isinstance(fl, str):
        out["file_log_tail"] = fl[-3000:].splitlines()[-40:]
    for a in (tl.get("audit_excerpts") or [])[-30:]:
        if isinstance(a, dict):
            out["audit_tail"].append(
                {
                    "event_type": a.get("event_type"),
                    "trace_id": a.get("trace_id"),
                    "preview": str(a.get("payload") or a)[:400],
                }
            )
        else:
            out["audit_tail"].append(str(a)[:400])
    blob = json.dumps(tl, ensure_ascii=False)
    out["blob_flags"] = {
        "has_plan_sql": "plan_sql" in blob.lower(),
        "has_data_agent": "data_agent" in blob.lower() or "fetches=" in blob,
        "has_resolve_products": "resolve_products" in blob,
        "has_query_rows": "query_rows" in blob,
        "has_fetch_sale_lines": "fetch_sale_lines" in blob,
        "has_tool_selector": "tool_selector" in blob or "tool-selector" in blob,
        "has_data_agent_turn": "data_agent_turn" in blob,
        "has_tool_selector_suggest": "tool_selector_suggest" in blob,
        "has_trans_code_113": "TRANS_CODE='113'" in blob or "TRANS_CODE = '113'" in blob,
        "has_planner_failed": "planner_failed" in blob,
        "has_partial": "partial" in blob.lower(),
        "audit_excerpt_count": len(tl.get("audit_excerpts") or []),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
