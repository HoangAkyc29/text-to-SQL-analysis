# Select tables — first phase before plan_sql

## Goal

Choose **only** the logical tables needed for the brief. Do **not** write SQL, WHERE filters, joins, or aggregations in this phase.

## Output JSON

```json
{
  "action": "select_tables",
  "selected_tables": ["SKU_DEF", "STRANS", "TRANSHDR"],
  "selected_target_dbs": ["db2", "db2", "db2"],
  "reasoning": "short why these tables"
}
```

Rules:

- `len(selected_tables) <= 6` and non-empty (unless `clarify` / `impossible`).
- Names must appear in `schema_context` / `logical_tables` / retrieval tables (bare names: `STRANS`, `SKU_DEF` — not `db2.dbo.STRANS`).
- Optional `selected_target_dbs[i]` parallel to each table (`db1` or `db2`). Prefer **db2** for master + current fact; **db1** only when `shard_plan` / time range needs historical shards.
- For historical fact tables (`STRANS` / `PMTRANS`), set `selected_target_dbs` to `db1` when `shard_plan.needs_db1`. Physical `_YYYYMM` names are chosen later in `plan_sql` from `shard_plan.shards` — do **not** invent suffixes here. db2 always uses bare logical names.
- On retry: if `shard_plan.needs_db2` and not `needs_db1`, keep `selected_target_dbs` on **db2** for fact tables even if prior risk text claimed “historical”. Do **not** flip to db1 from vague feedback alone.
- If omitted, pipeline still infers from `shard_plan`.
- Prefer grain-correct set: resolve product → master (`SKU_DEF`/`BARCODE`); bill/sale lines → `STRANS` (± `TRANSHDR`); payments → `PMTRANS`; loyalty card → `CSCARD` / `CRDTRANS`.
- Do **not** invent tables. Do **not** emit `plan_sql` / `probe_sql` / `sql_queries` in this phase.
- Still allowed: `action: "clarify"` or `action: "impossible"` with the usual fields when the brief cannot be scoped to tables.

## After this phase

The pipeline attaches static `inbox.table_samples` (5 example rows per selected table). You will then be called again with `mode=plan_sql` to write SQL using those samples as grain/value context.
