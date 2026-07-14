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
- Prefer grain-correct set: resolve product → master (`SKU_DEF`/`BARCODE`); bill/sale lines → `STRANS` (± `TRANSHDR`); payments → `PMTRANS`; loyalty card → `CSCARD` / `CRDTRANS`.
- Do **not** invent tables. Do **not** emit `plan_sql` / `probe_sql` / `sql_queries` in this phase.
- Still allowed: `action: "clarify"` or `action: "impossible"` with the usual fields when the brief cannot be scoped to tables.

## After this phase

The pipeline attaches static `inbox.table_samples` (5 example rows per selected table). You will then be called again with `mode=plan_sql` to write SQL using those samples as grain/value context.
