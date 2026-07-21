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
    "db_error_feedback": {},
    "risk_feedback": {
      "query_index": 0,
      "purpose": "metric_by_dimension",
      "concerns": ["ambiguous_fact_join_grain"],
      "issue": "...",
      "suggestion": "...",
      "rejected_sql": "SELECT ...",
      "target_db": "db2"
    },
    "risk_rejections": [],
    "probe_mode": false,
    "table_samples": [
      {
        "table": "<selected table>",
        "data_source": "<selected database>",
        "columns": ["<column_a>", "<column_b>"],
        "rows": [{"<column_a>": "<sample value>", "<column_b>": "<sample value>"}],
        "row_count": 5
      }
    ]
  },
  "attempt": 1,
  "schema_context": { "tables": [], "domain_definitions_excerpt": "...", "logical_tables": [] },
  "retrieval_context": {
    "phase": "hierarchical",
    "columns": [{"semantic_key": "<retrieved semantic key>", "text": "...", "score": 0.82, "tables": [], "facts_excerpt": "..."}],
    "tables": [{"table_ref": "<database:table>", "text": "...", "score": 0.75, "join_hints": []}],
    "case_studies": [{"text": "...", "score": 0.7, "links": []}],
    "candidate_tables": ["<database:table>"],
    "candidate_semantic_keys": ["<semantic key>"]
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
    {
      "role": "main|probe",
      "purpose": "descriptive_snake_case",
      "subtask_id": "st-optional",
      "requirement_ids": ["metric:0", "filter:0"]
    },
    "..."
  ],
  "target_dbs": ["db2", "db1"],
  "target_db": "db2",
  "reasoning": "short explanation",
  "attempt": 1,
  "schema_tables_used": ["<selected table>"],
  "semantic_keys_used": ["<retrieved semantic key>"]
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
- Every `query_meta[]` must list the exact `brief.requirements[].requirement_id` values evidenced by that query. Inferred optional requirements must not displace explicit required ones.
- On retry, `inbox.retry_directive` is authoritative:
  - Change only queries serving `must_fix_requirement_ids`; preserve already satisfied deliverables.
  - Each `required_evidence[]` entry states which user-visible evidence columns or ranking keys must be projected.
  - The new plan must materially differ from `prior_plan_fingerprint`; resubmitting the same predicates/projections is rejected before execution.
  - Never answer a missing-value-evidence gap by merely renaming an internal key. Project the requested value or a runtime-grounded mapping between that value and the internal key.
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
- Prefer several small `sql_queries` with distinct `query_meta[].purpose` when deliverables conflict in grain (see **Deliverable decomposition** below); do not collapse incompatible answer shapes into one deep CTE + window.

## Deliverable decomposition (mandatory thinking before SQL)

You are not asked to “pull related rows.” You are asked to produce **result sets that can each answer a distinct user-facing question** after Agent IV reads them. Pipeline executes **every** entry in `sql_queries` (≤ 6). One query that partially overlaps two asks is a planning failure if either ask cannot be answered truthfully from that result alone.

### Step A — Inventory answer obligations

Before writing any `WITH`/`SELECT`, build an internal checklist from the brief (and `brief.plan.subtasks` / `retrieval_facets` when present):

1. **Measurement asks** — totals, counts, sums, averages (“how much / how many / tổng / số lượng”). These need a **stable aggregation grain** (e.g. per product, per store, per day).
2. **Existence / validity filters** — thresholds and membership rules that *constrain* which facts count (e.g. bill total ≥ X). Filters are shared context; they are **not** themselves a substitute for a measurement ask.
3. **Enumeration / ranking asks** — “list”, “top N”, “gần nhất”, “mới nhất”, sample bills/lines. These need an **ordered window or ORDER BY + TOP** at a grain that matches the list unit (usually bill or line), not a collapsed total.
4. **Resolution asks** — map user codes → internal keys (SKU, barcode, card). Prefer `role: "probe"` only when keys are still unknown; after probe success, fact queries use resolved keys.

Each distinct obligation in (1) or (3) is a **deliverable**. Shared filters (2) and time_range apply to all deliverables unless the brief scopes them differently.

### Step B — Test grain compatibility

Ask: *If I keep only one result table, can a careful analyst answer every deliverable without guessing?*

- **Compatible** → one `main` query is enough (same grain, same filters; e.g. daily revenue by store only).
- **Incompatible** → you need **separate `main` queries**. Classic conflict: an **aggregate over the full filtered population** versus a **ranked subset** (top-N / nearest N). Rows that survive `ROW_NUMBER() … <= N` are not the population for “total quantity over the period.” Embedding both in one CTE that truncates to N **silently drops** the measurement deliverable.
- **Orthogonal slices** (different metrics or different entity grains) → separate queries even if they share joins; Agent IV merges artifacts, SQL Server does not need one mega-statement.

### Step C — Map deliverables → `sql_queries` / `query_meta`

For each deliverable emit one statement (or a minimal probe + mains):

| Deliverable kind | `query_meta.role` | `query_meta.purpose` (descriptive snake_case) | Result shape |
|------------------|-------------------|-----------------------------------------------|--------------|
| Period / cohort totals | `main` | e.g. `qty_by_product_period` | One row per aggregation key; no top-N truncation of the population |
| Ranked / nearest list | `main` | e.g. `top_n_bills_per_product` | Window or ordered list; N applies **only** here |
| Key resolution | `probe` | e.g. `resolve_product_codes` | Small lookup; then fact mains |

- `len(sql_queries) == len(query_meta) == len(target_dbs)`.
- Reuse the same joins/filters across mains when they share scope; **do not** reuse a truncated ranking query as the totals query.
- If `brief.plan.subtasks` exists, align `query_meta[].subtask_id` (or purpose text) to those subtasks so coverage is auditable.

### Step D — Pre-emit coverage check (write into `reasoning`)

`reasoning` must briefly state:

1. The deliverable checklist you derived (measurement / list / probe).
2. Which `sql_queries[i]` satisfies which deliverable.
3. Why any single-query plan is sufficient **or** why grains forced a split.

If you cannot point each brief obligation to a query, revise the plan before responding — do not hope Agent IV will “infer” missing totals from a top-N sample.

### Anti-pattern (conceptual)

Collapsing “total over period” and “N nearest bills” into one ranked CTE so that `rn <= N` rows are treated as the full answer set. That pattern optimizes for list shape and **falsifies** the measurement ask. Split them.

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
    "reason": "missing_business_definition | missing_time_range | ambiguous_identifier | ...",
    "partial_brief": { "...current brief..." },
    "questions": [
      {
        "id": "<question_id>",
        "prompt": "<specific information needed from the user>",
        "options": [
          {"id": "<choice>", "label": "<user-facing choice>", "brief_value": {"filters": {"<brief_key>": "<value>"}}},
          {"id": "unknown", "label": "Không chắc — khám phá dữ liệu", "brief_value": {"exploration_mode": true, "user_knowledge_level": "unknown"}}
        ],
        "maps_to_brief_field": "filters.<brief_key>",
        "reusable_fact": false,
        "fact_type": "definition",
        "fact_scope": "user",
        "schema_links": []
      }
    ]
  }
}
```

Emit `clarify` on attempt 1 when:
- A required business definition is missing and not `exploration_mode`.
- Multiple plausible grains/filters and guessing would change the answer set.
- Informal user codes without technical terms — prefer clarify over assuming expert.

Set `reusable_fact: true` only when the question asks for a reusable declarative
domain meaning rather than a value that applies only to the current request.
Such a question must include grounded `schema_links` from the retrieved
dictionary context. Keep `fact_scope: user` unless the authenticated reviewer
promotes it later. Never place the resulting business fact or ready-made SQL in
this guide.

## Probe-once-then-fact (mandatory)

When `inbox.data_feedback.issue` is `probe_success_needs_fact` or a prior attempt returned probe rows:
1. **Do not** emit another probe-only `probe_sql` plan.
2. Emit `plan_sql` with at least one `query_meta[].role: "main"` fact query.
3. Use resolved keys from probe (e.g. `SKU_ID`) on fact tables — not raw unresolved user codes when probe already succeeded.
4. Join/filter using column facts + case studies; keep grain consistent with the brief.
5. For top-N windows when brief asks: `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`.

Always set `reasoning` explaining the role of each query (`probe` vs `main`) and which user deliverable each `main` covers (see **Deliverable decomposition**).

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

### Risk feedback (III → II) — mandatory when present

Agent III may reject SQL that already passed PolicyEngine. The pipeline then retries you with:

- `inbox.risk_rejections[]` — **all** rejections from the prior attempt (one per failed `sql_queries[i]`; do not ignore all but the last).
- `inbox.risk_feedback` — the **latest** rejection record (same shape as one list element; convenience pointer).

Each record typically includes: `query_index`, `purpose`, `concerns[]`, `issue`, optional `suggestion`, `rejected_sql`, `target_db`.

#### How to think (before rewriting SQL)

1. **Inventory which deliverables broke** — Map each rejection to the `purpose` / deliverable from your prior plan (or to `query_index` if purpose missing). A multi-query plan may need several mains fixed, not one mega-rewrite that re-collapses grains.
2. **Classify the signal** (use `concerns` + `issue` + `suggestion` as hints, not as copy-paste SQL):
   - **Join / grain** — header↔line (or fact↔fact) keys incomplete or ambiguous relative to `schema_context` / column facts / table join hints. Re-read dictionary join keys; align ON clauses with the documented grain.
   - **Document-type / transaction-code scope** — fact tables often carry multiple document kinds. If III flags missing type/code filter, constrain using **brief + domain excerpt + column/case-study retrieval** — choose codes that match the metric/intent. **Do not** invent a default code or paste a fixed literal from memory when the brief/RAG does not support it.
   - **Wrong fact table / metric mismatch** — wrong source for the asked measure; re-ground from hierarchical columns + domain excerpt.
   - **Performance / scan** — missing selective predicates (time, store, keys); tighten filters already present in the brief.
   - **Topology / DB routing** — **trust `schema_context.shard_plan` over III prose.** If `needs_db2` and not `needs_db1`, keep bare fact names on **db2**. Do **not** switch to db1 or invent `_YYYYMM` suffixes because a concern says “historical” or “outside db2”. Only use monthly shards when `needs_db1` and prefer exactly `shard_plan.shards` (≤ `archive_newest_ym`).
3. **Apply fixes per rejection** — For each item in `risk_rejections`, change the corresponding `main`/`probe` so that concern is addressed. Shared CTEs may be reused, but do not “fix” one query and leave the sibling deliverable broken.
4. **Do not** paste `suggestion` text into SQL. Treat it as reasoning guidance; emit valid T-SQL only.
5. **`reasoning` on retry** must name the concerns you addressed and which `sql_queries[i]` / `purpose` each fix belongs to.
6. **Ignore vacuous topology pressure** — If inbox suggestion restates that db2 bare names are correct for this `shard_plan`, do not “fix” by moving facts to db1.

If `risk_rejections` is empty but `risk_feedback` is set, treat that single object as a one-element list.

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
