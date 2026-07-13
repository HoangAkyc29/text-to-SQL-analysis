#!/usr/bin/env python3
"""Summarize recent audit.jsonl events (run inside chat-gateway or with mounted data)."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

p = Path(sys.argv[1] if len(sys.argv) > 1 else "/app/data/state/audit.jsonl")
events: list[dict] = []
with p.open(encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            continue

for e in events[-50:]:
    tid = (e.get("trace_id") or "")[:8]
    et = e.get("event_type")
    at = e.get("at", "")
    pl = e.get("payload") or {}
    extra = ""
    if et == "agent_ii_plan":
        qs = pl.get("queries") or []
        roles = ",".join((q.get("query_meta") or {}).get("role", "?") for q in qs)
        extra = f" queries={len(qs)} attempt={pl.get('sql_attempt')} roles={roles}"
    elif et == "sql_execute":
        extra = f" outcome={pl.get('outcome')} rows={pl.get('row_count')} db={pl.get('target_db')}"
    elif et == "sql_policy_reject":
        extra = f" viol={pl.get('violations')}"
    elif et in ("agent_i_route", "pipeline_outcome", "agent_timeout", "error", "workflow"):
        keys = list(pl.keys())[:6]
        extra = " " + str({k: pl.get(k) for k in keys})[:160]
    print(f"{at} {et} {tid}{extra}")

print("--- unique recent traces ---")
c = Counter((e.get("trace_id") or "")[:8] for e in events[-100:])
print(c.most_common(12))

# Dump latest trace detail
if events:
    latest_tid = events[-1].get("trace_id")
    print(f"\n=== full events for latest trace {latest_tid} ===")
    for e in events:
        if e.get("trace_id") != latest_tid:
            continue
        et = e.get("event_type")
        pl = e.get("payload") or {}
        if et == "agent_ii_plan":
            print(f"\n[{et}] attempt={pl.get('sql_attempt')} target_db={pl.get('target_db')}")
            print("reasoning:", (pl.get("reasoning") or "")[:500])
            for q in pl.get("queries") or []:
                meta = q.get("query_meta") or {}
                print(f"  q{q.get('query_index')} role={meta.get('role')} purpose={meta.get('purpose')}")
                print(f"    sql: {(q.get('sql') or '')[:400]}")
        elif et == "sql_execute":
            print(
                f"[{et}] outcome={pl.get('outcome')} rows={pl.get('row_count')} "
                f"db={pl.get('target_db')} sql={(pl.get('sql') or '')[:200]}"
            )
        else:
            print(f"[{et}] {json.dumps(pl, ensure_ascii=False)[:300]}")
