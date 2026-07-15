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

## Reject criteria

- Policy blocked.
- Wrong fact table for metric (e.g. loyalty points taken from the wrong grain/table).
- Unbounded cross join pattern.
- Exporting sensitive columns without business need.

## Domain codes & metrics

**Do not** hardcode retail document codes or join recipes here. Read `schema_context.domain_definitions_excerpt`, table/column facts, and retrieval context. Reject when SQL contradicts those sources.