# Plan SQL — primary decide path

## Input payload

```json
{
  "brief": { "...AnalysisBrief..." },
  "inbox": { "policy_feedback": {}, "data_feedback": {}, "probe_mode": false },
  "attempt": 1,
  "schema_context": { "tables": [], "domain_definitions_excerpt": "...", "logical_tables": [] },
  "retrieval_context": ["(0.82) case study text...", "..."]
}
```

## Output: `plan_sql`

```json
{
  "action": "plan_sql",
  "sql_queries": ["SELECT TOP 50000 ...", "..."],
  "query_meta": [
    {"role": "main|probe", "purpose": "vip_revenue|inventory|...", "subtask_id": "st-optional"},
    "..."
  ],
  "target_dbs": ["db2", "db1"],
  "target_db": "db2",
  "reasoning": "short explanation",
  "attempt": 1,
  "schema_tables_used": ["STRANS", "PMTRANS"]
}
```

Rules:
- `len(sql_queries)` == `len(target_dbs)` == `len(query_meta)` (≤ 6).
- Default fact queries on **db2**; use **db1** shards only when `time_range` needs history before cutoff.
- Master lookups (SKU, barcode, card) → **db2**.
- Use `FORMAT(TRAN_DATE,'yyyy-MM')` for monthly grain.
- VIP revenue: join `CSCARD` + `PMTRANS`, filter `card_prefix` via `CARD_ID LIKE 'E%'` when in filters.
- Apply `STK_ID IN (...)` when `brief.filters.STK_ID` or store scope present.

## Output: `clarify`

```json
{
  "action": "clarify",
  "clarification_request": {
    "reason": "missing_vip_definition | missing_time_range | ambiguous_product | ...",
    "partial_brief": { "...current brief..." },
    "questions": [
      {
        "id": "vip_card_prefix",
        "prompt": "VIP được định nghĩa thế nào?",
        "options": [
          {"id": "prefix_e", "label": "Thẻ bắt đầu E", "brief_value": {"filters": {"card_prefix": "E"}}},
          {"id": "unknown", "label": "Không chắc — khám phá dữ liệu", "brief_value": {"exploration_mode": true, "user_knowledge_level": "unknown"}}
        ],
        "maps_to_brief_field": "filters.card_prefix"
      }
    ]
  }
}
```

Emit `clarify` on attempt 1 when VIP intent lacks `card_prefix`/`loyalty_tier` and not `exploration_mode`.

## Output: `impossible`

```json
{
  "action": "impossible",
  "reason": "human readable",
  "missing_capabilities": ["cross_db_join_on_server", "table_not_in_dictionary"]
}
```

## Retry (`attempt` > 1)

- Read `inbox.policy_feedback.violations` — fix table/column issues.
- Read `inbox.data_feedback` — adjust grain, widen time, add probes (see `probe_feedback_guide.md`).
- Do not repeat identical SQL.

## Retrieval context

When `retrieval_context` contains similar SQL templates:
- Reuse join patterns and `TRANS_CODE` filters.
- Re-parameterize dates, `STK_ID`, card prefix from current `brief`.
- Prefer promoted case studies over inventing new join paths.
