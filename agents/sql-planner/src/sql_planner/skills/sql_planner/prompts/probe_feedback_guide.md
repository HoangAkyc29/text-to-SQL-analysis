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
| `grain` | Drop aggregation — line-level `STRANS` sample |
| `needs_sql_retry` | Adjust filters per `suggested_intent_fix` |

## Exploration mode

When `brief.exploration_mode` or `user_knowledge_level: unknown`:
- Emit 2–3 exploratory queries: monthly trend, by store, SKU sample.
- Mark `query_meta[].purpose` clearly.

## Product code path

If `filters.product_code` or `filters.sku`:
1. Probes on `SKU_DEF`, `BARCODE` (db2).
2. Main revenue on `STRANS` with resolved `SKU_ID` predicate.
