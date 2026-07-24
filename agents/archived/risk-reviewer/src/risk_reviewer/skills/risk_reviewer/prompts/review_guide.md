# SQL review task

## Input payload

```json
{
  "sql": "SELECT TOP 50000 ...",
  "allowed_tables": ["STRANS", "PMTRANS"],
  "schema_context": { "tables": [], "domain_definitions_excerpt": "..." },
  "policy_result": { "allowed": true, "violations": [] }
}
```

`policy_result` is pre-computed — **do not contradict** `allowed: false`.

## Output schema

```json
{
  "verdict": "approve | reject",
  "concerns": ["semantic_issue_or_policy_violation"],
  "risk_feedback": null,
  "schema_context_summary": {
    "table_count": 12,
    "has_domain_definitions": true
  }
}
```

When `verdict` is `reject`:
```json
"risk_feedback": {
  "issue": "wrong_fact_or_code_for_metric",
  "suggestion": "Align fact table and document codes with schema_context.domain_definitions_excerpt / column facts — do not invent codes"
}
```

## Approve criteria

- Policy allowed AND no severe semantic issues.
- Minor concerns (e.g. missing `TOP` but under row cap) → `approve` with concerns listed.

## Topology / cutoff (mandatory — read `schema_context.shard_plan`)

Before flagging `wrong_db_for_date_range`, `db1_shard_missing`, or “dates are historical / outside db2”:

1. Read `schema_context.shard_plan`: `cutoff`, `needs_db1`, `needs_db2`, `shards`, `archive_newest_ym`.
2. Read `schema_context.table_naming` (`as_of_date`, naming rules).
3. **Rule:** if `needs_db2` is true and `needs_db1` is false, the brief range is on the **live** side of cutoff. Bare `STRANS` / `PMTRANS` / `TRANSHDR` on **db2** is correct. Do **not** reject for wrong DB or demand db1 monthly shards.
4. Demand `STRANS_YYYYMM` only when `needs_db1` is true; suffixes must be ≤ `archive_newest_ym` / in `shard_plan.shards`. Never invent a month past `archive_newest_ym`.
5. Do **not** claim a table is missing from `allowed_tables` if that same name appears in the `allowed_tables` payload.

## Reject criteria

- Policy blocked.
- Wrong fact table for metric (e.g. loyalty points taken from the wrong grain/table).
- Unbounded cross join pattern.
- Exporting sensitive columns without business need.
- Real topology mismatch vs `shard_plan` (not inverted cutoff claims).

## Domain codes & metrics

**Do not** hardcode retail document codes or join recipes here. Read `schema_context.domain_definitions_excerpt`, table/column facts, and retrieval context. Reject when SQL contradicts those sources.