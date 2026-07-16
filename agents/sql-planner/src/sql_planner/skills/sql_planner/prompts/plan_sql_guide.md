# Plan SQL — primary decide path (after select_tables)

Pipeline calls you twice per SQL attempt:

1. `mode=select_tables` → list tables only (see `select_tables_guide.md`).
2. `mode=plan_sql` → this guide, with **`inbox.table_samples`** already attached.

## Input payload

```json
{
  "brief": { "...AnalysisBrief..." },
  "inbox": {
    "policy_feedback": {},
    "data_feedback": {},
    "probe_mode": false,
    "table_samples": [
      {
        "table": "STRANS",
        "data_source": "db2",
        "columns": ["STK_ID", "TRANS_NUM", "SKU_ID", "AMOUNT"],
        "rows": [{"STK_ID": "10001", "TRANS_NUM": "...", "SKU_ID": "...", "AMOUNT": 0}],
        "row_count": 5
      }
    ]
  },
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

## Using `table_samples`

- Samples illustrate **grain, column presence, and typical non-null values** for selected tables.
- Use them to avoid wrong joins / wrong filter columns.
- **Do not** hard-copy sample cell values into WHERE clauses unless the brief explicitly asks for those identifiers.
- Entries may include `error: sample_missing` — still plan from schema/RAG without inventing columns.

## Output: `plan_sql`

Do **not** emit `action: "select_tables"` in this phase.

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

1. Read **`retrieval_context.columns` first** — map brief terms to `semantic_key` and `facts_excerpt`.
2. Derive **candidate tables** from column `tables` refs and `candidate_tables`.
3. Confirm grain/join from column facts and table join hints.
4. Read **`retrieval_context.tables`** for join hints and column lists.
5. Prefer **`retrieval_context.case_studies`** with matching `links` for join/filter patterns and business formulas — **do not invent domain recipes in this guide**.
6. Emit `schema_tables_used` (logical names) and `semantic_keys_used` in your JSON response.

Legacy flat `retrieval_context` as `list[str]` is still supported — treat each string as a hint chunk.

## Rules (topology / policy only)

- `len(sql_queries)` == `len(target_dbs)` == `len(query_meta)` (≤ 6).
- Default fact queries on **db2** with **bare** names (`STRANS`, `PMTRANS`, `TRANSHDR`). **Do not** write `STRANS_YYYYMM` when `target_db=db2` or when `shard_plan.needs_db2` covers the range and `needs_db1` is false.
- Use **db1** monthly shards (`STRANS_YYYYMM` / `PMTRANS_YYYYMM`) **only** when `shard_plan.needs_db1` — prefer exactly `shard_plan.shards`; never invent a month past `shard_plan.archive_newest_ym` / `table_naming.archive_newest_ym`.
- Master lookups (SKU, barcode, card) → **db2** bare names.
- **Never** prefix tables with `db1.dbo.` or `db2.dbo.` — `target_db` selects the connection; use bare table names (`STRANS`, `TRANSHDR`, …).
- Only reference tables listed in `schema_context.logical_tables` / data_dictionary / expanded `db1_shards`. Do **not** invent table names (e.g. `rankedSales`, `productSkus`); use `WITH` CTEs or subqueries instead.
- Use `FORMAT(TRAN_DATE,'yyyy-MM')` for monthly grain when brief asks month grain.
- Apply `STK_ID IN (...)` when `brief.filters.STK_ID` or store scope is already in the brief (pipeline/role may also inject).
- Codes, formulas, VIP/gift/bill semantics → from `schema_context.domain_definitions_excerpt`, column facts, and **case studies** — not from hardcoded recipes in this file.
- Read `schema_context.table_naming` (as_of, cutoff, db2 bare vs db1 suffix rules).

## CTE / column hygiene (mandatory)

- Use only columns listed in `schema_context` / `inbox.table_samples` for the tables you query.
- Outer `ORDER BY` / `STRING_AGG … WITHIN GROUP (ORDER BY col)` / outer `SELECT` on a CTE alias require `col` in that CTE’s SELECT list.
- Prefer **multiple simple queries** (e.g. qty aggregate; bills ≥ threshold; top-N bill list) with clear `query_meta[].purpose` over one monolithic CTE.

## Text filters — substring + case-insensitive (mandatory)

For every **textual / code** predicate that would have been absolute equality:

- Use substring match and case-insensitivity: `LOWER(<column>) LIKE '%' + LOWER('<literal>') + '%'`.
- Multi-value → OR of such predicates (not absolute `IN` for codes/identifiers).
- Exceptions: numeric comparisons, date ranges, booleans.

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
- Required business definition is missing and not `exploration_mode` (VIP tier, bill validity rule, product id kind, store scope, etc.).
- Multiple plausible grains/filters and guessing would change the answer set.
- Informal user codes without technical terms — prefer clarify over assuming expert.

## Probe-once-then-fact (mandatory)

When `inbox.data_feedback.issue` is `probe_success_needs_fact` or a prior attempt returned probe rows:
1. **Do not** emit another probe-only `probe_sql` plan.
2. Emit `plan_sql` with at least one `query_meta[].role: "main"` fact query.
3. Use resolved keys from probe (e.g. `SKU_ID`) on fact tables — not raw unresolved user codes when probe already succeeded.
4. Join/filter using column facts + case studies; keep grain consistent with the brief.
5. For top-N windows when brief asks: `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`.

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

Read `inbox.db_error_feedback` when present (SQL ran then engine failed):
- `message`: SQL Server / ODBC error text (e.g. `Invalid column name 'TRAN_TIME'`)
- `rejected_sql`: the failing statement
- `target_db`, `query_index`
- `hints`: meta fix guidance — **apply the fix in new SQL; do not invent domain recipes**

Read `schema_context.product_resolution_hints` when present — raw product codes from the brief (`user_input`).

Read `schema_context.shard_plan` — `needs_db2` / `needs_db1` / `shards` / `cutoff` / `archive_newest_ym` for date routing.
Read `schema_context.table_naming` — db2 = bare names; db1 monthly suffix rolls with as_of.

### Policy violation cheat-sheet

| violation | Fix |
|-----------|-----|
| `logical_db_prefix_forbidden` | Remove `db1.`/`db2.` prefix; set `target_dbs` instead |
| `table_not_in_dictionary:X` | X is invented — use real table or CTE alias only inside WITH |
| `forbidden_pattern` | Single SELECT, no trailing `;` |

### DB error cheat-sheet

| message contains | Fix |
|------------------|-----|
| `Invalid column name` | Project the column in the CTE/SELECT that owns the alias; or pick a real column from schema/samples |
| `Invalid object name` | Bare dictionary name; no invented `_YYYYMM` on db2 |
| syntax / STRING_AGG | Simplify; ensure ORDER BY cols exist on the aggregated source |

- Read `inbox.data_feedback` — adjust grain, widen time, add probes (see `probe_feedback_guide.md`).
- Do not repeat identical SQL.

## Retrieval context

Structured hierarchical payload (preferred) or legacy flat strings.

When hierarchical:
- Phase 1 columns define **which data points** matter and their **semantic grain**.
- Phase 2 tables confirm **where** those columns live and how to join.
- Case studies with `links` matching your semantic keys are high-trust patterns — **parameterize** dates/filters from current `brief`; do not copy unrelated templates blindly.

When flat list of strings:
- Reuse join patterns from retrieved text.
- Re-parameterize dates, `STK_ID`, card prefix from current `brief`.
- Prefer promoted case studies over inventing new join paths.
