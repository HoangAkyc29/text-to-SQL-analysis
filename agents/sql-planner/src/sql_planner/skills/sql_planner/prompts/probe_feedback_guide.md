# Probe & data feedback

## `probe_sql` action

When `inbox.probe_mode` or `inbox.data_feedback.probe_requests` is set:

```json
{
  "action": "probe_sql",
  "sql_queries": ["SELECT TOP 100 ...", "..."],
  "query_meta": [{"role": "probe", "purpose": "product_lookup"}, "..."],
  "target_dbs": ["db2", "db2"],
  "reasoning": "IV-requested probes"
}
```

Probe SQL should be **small** (`TOP 100`–`1000`), read-only, aimed at resolving ambiguity.

## Common `data_feedback.issue` values

| Issue | Planner response |
|-------|------------------|
| `empty_result` | Widen time range; check wrong `TRANS_CODE`; add SKU/barcode probe |
| `identifier_mismatch` | Probe `SKU_DEF`/`BARCODE`; fix predicate on `SKU_ID` not user barcode |
| `probe_success_needs_fact` | Stop probing — emit `plan_sql` with `role: main` STRANS+TRANSHDR fact query using SKU_ID from probe |
| `grain` | Drop aggregation — line-level `STRANS` sample |
| `needs_sql_retry` | Adjust filters per `suggested_intent_fix` |

## `inbox.db_error_feedback` (execute failed)

When present, SQL passed policy/review but the engine rejected it:

```json
{
  "error": "db_error",
  "message": "Invalid column name 'TRAN_TIME'.",
  "rejected_sql": "WITH …",
  "target_db": "db2",
  "hints": ["…"]
}
```

Fix the **engine** issue (missing CTE columns, bad object name, syntax). Prefer splitting into simpler queries. Do **not** invent domain SQL recipes from hints.

## Exploration mode

When `brief.exploration_mode` or `user_knowledge_level: unknown`:
- Emit 2–3 exploratory queries: monthly trend, by store, SKU sample.
- Mark `query_meta[].purpose` clearly.

## Product code path

If `filters.product_code` or `filters.sku`:
1. Probes on `SKU_DEF`, `BARCODE` (db2).
2. Main revenue on `STRANS` with resolved `SKU_ID` predicate.
