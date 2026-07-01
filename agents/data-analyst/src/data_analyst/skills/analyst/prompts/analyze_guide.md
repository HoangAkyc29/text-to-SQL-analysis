# Analyze datasets — output contract

## Success payload

```json
{
  "action": "complete | partial",
  "headline_metrics": {"row_count": 1000, "preview_rows_1": 30},
  "artifact_paths": ["/path/to/out/st-vip/st-vip_summary.csv"],
  "caveats": ["st-inv:weak_match:0.21"],
  "sandbox_steps": 3,
  "coverage": {
    "diagnosis": "full | partial",
    "reused": ["recipe:tool-id@0.82"],
    "generated": ["step:uuid"],
    "gaps": [],
    "subtask_status": {"st-vip": "reuse"}
  },
  "new_steps": []
}
```

## `data_feedback` payload

```json
{
  "action": "data_feedback",
  "data_feedback": {
    "needs_sql_retry": true,
    "issue": "empty_result | identifier_mismatch | grain",
    "summary": "Vietnamese explanation",
    "diagnosis": "short code",
    "suggested_intent_fix": "wider filters or probe SKU",
    "probe_requests": [
      {"purpose": "sku_lookup", "suggested_sql": "SELECT TOP 100 ..."}
    ],
    "expected_vs_observed": {
      "expected": "rows for SKU 123456",
      "observed": "0 main, 3 probe"
    }
  }
}
```

## Identifier mismatch

When `main_rows == 0` but product probe returns rows:
- Issue = `identifier_mismatch`
- Do not claim zero sales — ask II to fix SKU resolution.

## Exploration clarify

When `brief.exploration_mode` and data exists but intent still vague:
- `action` may include clarify suggestion (runtime: `suggest_clarify` path).

## Charts

If `brief.output_format` contains `chart` and ≥2 numeric columns exist, emit `chart.png` via `plot_chart`.

## Partial outcomes

`action: partial` when `coverage.diagnosis == partial` — still return artifacts for successful subtasks.

## Budget

Respect `max_steps` (default 8). Stop with `coverage.gaps` entry `budget_exceeded:*` when capped.
