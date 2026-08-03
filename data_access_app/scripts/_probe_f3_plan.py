"""Print F3 dual-query plan for the UI filters from the hang screenshot."""
from __future__ import annotations

from datetime import date, datetime

from app.db.cutoff import split_date_range
from app.db.dual_query import plan_strans_parts
from app.domain.columns import BILL_VALUE_SQL

now = datetime(2026, 7, 27)  # matches DATA_ACCESS_AS_OF in native_run.log
ds, de = date(2020, 2, 1), date(2024, 8, 3)
stores = ["10001", "10004", "10005"]

split = split_date_range(ds, de, now=now)
print("as_of", now.date())
print("cutoff", split.cutoff)
print("archive_newest_ym", split.archive_newest_ym)
print("needs_db1", split.needs_db1, "needs_db2", split.needs_db2)
print("db1_range", split.db1_start, "->", split.db1_end)
print("db2_range", split.db2_start, "->", split.db2_end)
print("strans_shards", len(split.strans_shards), split.strans_shards)
print("NOTE: shards only exist from", "202312", "— years 2020-2022 are NOT queried")

extra = ["CARD_ID IS NOT NULL", "LTRIM(RTRIM(CARD_ID)) <> ''"]
params: list = []
placeholders = ",".join("?" for _ in stores)
extra.append(f"LTRIM(RTRIM(STK_ID)) IN ({placeholders})")
params.extend(stores)

body = f"""
        SELECT
            LTRIM(RTRIM(CARD_ID)) AS CARD_ID,
            LTRIM(RTRIM(STK_ID)) AS STK_ID,
            LTRIM(RTRIM(TRANS_NUM)) AS TRANS_NUM,
            {BILL_VALUE_SQL} AS line_total
        FROM {{table}}
        WHERE 1=1
    """
parts = plan_strans_parts(split, body, extra_where=" AND ".join(extra), extra_params=params)
print("n_sql_parts", len(parts))
print()
for i, (target, sql, p) in enumerate(parts, 1):
    print("=" * 72)
    print(f"#{i} target={target}")
    print(f"params={p}")
    print(sql.strip())
