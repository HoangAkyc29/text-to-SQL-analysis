"""Summarize latest query_log cluster."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

p = Path(r"E:\CODING STUFF\PROJECT\Data Extracting\test sample\query_log.txt")
text = p.read_text(encoding="utf-8", errors="replace")
blocks = re.split(r"(?=^\[\d{4}-\d{2}-\d{2} )", text, flags=re.M)
events: list[dict] = []
for b in blocks:
    b = b.strip()
    if not b:
        continue
    m = re.match(r"\[(.+?)\] (START|OK|ERROR) target=(\w+)", b)
    if not m:
        continue
    ts, ph, tg = m.groups()
    fm = re.search(r"FROM\s+(\S+)", b, re.I)
    pm = re.search(r"PARAMS:\s*(.+)", b)
    rows = re.search(r"ROWS:\s*(\d+)", b)
    ms = re.search(r"ELAPSED_MS:\s*([\d.]+)", b)
    err = re.search(r"ERROR:\s*(.+)", b)
    events.append(
        {
            "ts": ts,
            "ph": ph,
            "tg": tg,
            "tbl": fm.group(1) if fm else None,
            "params": pm.group(1).strip() if pm else None,
            "rows": int(rows.group(1)) if rows else None,
            "ms": float(ms.group(1)) if ms else None,
            "err": err.group(1).strip() if err else None,
        }
    )

pairs: list[tuple[dict, dict | None]] = []
i = 0
while i < len(events):
    e = events[i]
    if e["ph"] == "START":
        nxt = events[i + 1] if i + 1 < len(events) else None
        if nxt and nxt["ph"] in ("OK", "ERROR"):
            pairs.append((e, nxt))
            i += 2
        else:
            pairs.append((e, None))
            i += 1
    else:
        i += 1


def parse(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")


clusters: list[list[tuple[dict, dict | None]]] = []
cur: list[tuple[dict, dict | None]] = []
for e, o in pairs:
    if not cur:
        cur = [(e, o)]
        continue
    prev = parse(cur[-1][0]["ts"])
    now = parse(e["ts"])
    if (now - prev).total_seconds() > 45:
        clusters.append(cur)
        cur = [(e, o)]
    else:
        cur.append((e, o))
if cur:
    clusters.append(cur)

run = clusters[-1]
print(f"=== Latest cluster: {len(run)} queries ===")
print(f"time: {run[0][0]['ts']} -> {run[-1][0]['ts']}")
print()
sum_rows = 0
sum_ms = 0.0
pending = 0
for e, o in run:
    st = e["tbl"] or "?"
    if o is None:
        print(f"{e['ts']}  RUN   {e['tg']:4} {st:16}")
        pending += 1
        continue
    rows = o["rows"] if o["rows"] is not None else "-"
    ms = f"{o['ms']:.0f}" if o["ms"] is not None else "-"
    print(f"{e['ts']}  {o['ph']:5} {e['tg']:4} {st:16} rows={rows!s:<10} ms={ms}")
    if isinstance(o["rows"], int):
        sum_rows += o["rows"]
    if isinstance(o["ms"], float):
        sum_ms += o["ms"]
    if o.get("err"):
        print(f"         ERROR: {o['err']}")

print()
print(f"total_rows={sum_rows:,}  sql_time_sum={sum_ms/1000:.1f}s  still_running={pending}")
# show first STRANS params in this run
for e, o in run:
    if e.get("tbl") and "STRANS" in e["tbl"].upper() and e.get("params"):
        print(f"STRANS params sample: {e['params']}")
        break
# CSCARD count
n_cs = sum(1 for e, _ in run if e.get("tbl") and "CSCARD" in e["tbl"].upper())
n_st = sum(1 for e, _ in run if e.get("tbl") and "STRANS" in e["tbl"].upper())
print(f"breakdown: STRANS-like={n_st}  CSCARD={n_cs}")
