# Plan SQL — primary decide path

## Input payload

```json
{
  "brief": { "...AnalysisBrief..." },
  "inbox": { "policy_feedback": {}, "data_feedback": {}, "probe_mode": false },
  "attempt": 1,
  "schema_context": { "tables": [], "domain_definitions_excerpt": "...", "logical_tables": [] },
  "retrieval_context": {
    "phase": "hierarchical",
    "columns": [{"semantic_key": "amount_bill_header", "text": "...", "score": 0.82, "tables": [], "facts_excerpt": "..."}],
    "tables": [{"table_ref": "db2:strans", "text": "...", "score": 0.75, "join_hints": []}],
    "case_studies": [{"text": "...", "score": 0.7, "links": []}],
    "candidate_tables": ["db2:strans", "db2:transhdr"],
    "candidate_semantic_keys": ["sku_id", "amount_bill_header", "trans_code"]
  }
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
  "schema_tables_used": ["STRANS", "TRANSHDR"],
  "semantic_keys_used": ["sku_id", "amount_bill_header", "trans_code"]
}
```

## Column-first reasoning (hierarchical retrieval)

When `retrieval_context.phase` is `hierarchical`:

1. Read **`retrieval_context.columns` first** — map brief terms (bill, SKU, quantity, gift) to `semantic_key` and `facts_excerpt`.
2. Derive **candidate tables** from column `tables` refs and `candidate_tables`.
3. Confirm grain/join from column facts (`amount_bill_header` = TRANSHDR.AMOUNT for min bill; `amount_line_item` = STRANS line).
4. Read **`retrieval_context.tables`** for join hints and column lists.
5. Check **`retrieval_context.case_studies`** with matching `links` for SQL patterns.
6. Emit `schema_tables_used` (logical names) and `semantic_keys_used` in your JSON response.

Legacy flat `retrieval_context` as `list[str]` is still supported — treat each string as a hint chunk.
```

Rules:
- `len(sql_queries)` == `len(target_dbs)` == `len(query_meta)` (≤ 6).
- Default fact queries on **db2**; use **db1** shards only when `time_range` needs history before cutoff.
- Master lookups (SKU, barcode, card) → **db2**.
- **Never** prefix tables with `db1.dbo.` or `db2.dbo.` — `target_db` selects the connection; use bare table names (`STRANS`, `TRANSHDR`, …).
- Only reference tables listed in `schema_context.logical_tables` / data_dictionary. Do **not** invent table names (e.g. `rankedSales`, `productSkus`); use `WITH` CTEs or subqueries instead.
- Multi-SKU gift queries with min bill value: probe `SKU_DEF`, join `STRANS` to `TRANSHDR` on `TRANS_NUM`, filter `TRANSHDR.AMOUNT >= min_bill`, `TRANS_CODE='113'`.
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

Emit `clarify` on attempt 1 when:
- VIP intent lacks `card_prefix`/`loyalty_tier` and not `exploration_mode`.
- Multiple `product_code` values (list ≥2) **and** (`min_bill_value` or `min_transaction_value` in filters) — ask: mã hàng là SKU nội bộ hay barcode? Bill hợp lệ = tổng TRANSHDR.AMOUNT?
- Bill validity rule ambiguous (header total vs line sum vs payment) and `min_bill` in filters.
- User message uses informal product codes (7 digits) without technical terms — prefer clarify over assuming expert.

## Probe-once-then-fact (mandatory)

When `inbox.data_feedback.issue` is `probe_success_needs_fact` or a prior attempt returned probe rows:
1. **Do not** emit another probe-only `probe_sql` plan.
2. Emit `plan_sql` with at least one `query_meta[].role: "main"` fact query.
3. Use resolved `SKU_ID` from probe (not raw user code) on `STRANS`.
4. Join `TRANSHDR` on `TRANS_NUM`; filter `TRANSHDR.AMOUNT >= min_bill_value` when present.
5. For top-N per SKU: `ROW_NUMBER() OVER (PARTITION BY SKU_ID ORDER BY TRAN_DATE DESC)`.

Always set `reasoning` explaining the role of each query (`probe` vs `main`).

## Output: `impossible`

```json
{
  "action": "impossible",
  "reason": "human readable",
  "missing_capabilities": ["cross_db_join_on_server", "table_not_in_dictionary"]
}
```

## Retry (`attempt` > 1)

Read `inbox.policy_feedback` carefully — it now includes:
- `violations`: machine codes from PolicyEngine
- `rejected_sql`: the SQL that failed (learn from it, do not repeat)
- `hints`: Vietnamese guidance — **use hints to fix reasoning, do not paste hints as SQL**

Read `schema_context.product_resolution_hints` when present — pick a strategy and probe before fact query.

Read `schema_context.shard_plan` — `needs_db2` / `needs_db1` / `shards` / `cutoff` for date routing.

### Bill threshold + multi-SKU pattern (reasoning, not template)

When brief asks quantity per SKU **and** bill total threshold **and** top-N bills:
1. **Probe** `SKU_DEF`/`BARCODE` per `product_resolution_hints` — user code ≠ `SKU_ID`.
2. **Valid bills**: `TRANSHDR` where `TRANS_CODE='113'`, date in `time_range`, `AMOUNT >= min_bill` (header total).
3. **Gift lines**: `STRANS` join valid bills on `TRANS_NUM`, filter resolved `SKU_ID`, `TRANS_CODE='113'`.
4. **Top N per SKU**: `ROW_NUMBER() OVER (PARTITION BY SKU_ID ORDER BY TRAN_DATE DESC)` in a CTE — CTE names are local, not dictionary tables.
5. If unsure about bill total column or min_bill semantics → `clarify` on attempt 1.

### Policy violation cheat-sheet

| violation | Fix |
|-----------|-----|
| `logical_db_prefix_forbidden` | Remove `db1.`/`db2.` prefix; set `target_dbs` instead |
| `table_not_in_dictionary:X` | X is invented — use real table or CTE alias only inside WITH |
| `forbidden_pattern` | Single SELECT, no trailing `;` |

- Read `inbox.data_feedback` — adjust grain, widen time, add probes (see `probe_feedback_guide.md`).
- Do not repeat identical SQL.

## Retrieval context

Structured hierarchical payload (preferred) or legacy flat strings.

When hierarchical:
- Phase 1 columns define **which data points** matter and their **semantic grain**.
- Phase 2 tables confirm **where** those columns live and how to join.
- Case studies with `links` matching your semantic keys are high-trust patterns.

When flat list of strings:
- Reuse join patterns and `TRANS_CODE` filters.
- Re-parameterize dates, `STK_ID`, card prefix from current `brief`.
- Prefer promoted case studies over inventing new join paths.
