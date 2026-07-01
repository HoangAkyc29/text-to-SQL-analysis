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
  "issue": "wrong_trans_code_for_metric",
  "suggestion": "Use TRANS_CODE='113' on STRANS for retail revenue"
}
```

## Approve criteria

- Policy allowed AND no severe semantic issues.
- Minor concerns (e.g. missing `TOP` but under row cap) → `approve` with concerns listed.

## Reject criteria

- Policy blocked.
- Wrong fact table for metric (points on STRANS without card join).
- Unbounded cross join pattern.
- Exporting sensitive columns without business need.

## Vietnamese retail context

- Revenue retail: `STRANS` + `TRANS_CODE='113'`
- Payment at POS: `PMTRANS` + `TRANS_CODE='221'`
- Loyalty points: `CRDTRANS` / `CRDTRANS_ARC` + `811`/`812`
- Inventory: `STK_DTL`, not sales tables
