import json

tid = "ecbf1f0e"
with open("/app/data/state/audit.jsonl", encoding="utf-8") as f:
    events = [json.loads(line) for line in f if tid in line]
print("events", len(events))
for d in events:
    pl = d.get("payload") or {}
    et = d["event_type"]
    print(d.get("at"), et, pl.get("action"), pl.get("sql_attempt"), pl.get("outcome"), pl.get("row_count"), pl.get("violations"))
    if et == "agent_ii_plan":
        for q in pl.get("queries") or []:
            print("FULL SQL", q.get("query_index"), "len", len(q.get("sql") or ""))
            print(q.get("sql"))
            print("====")
    if et == "sql_policy_reject":
        print(pl.get("sql_preview") or pl.get("sql"))
