# LLM recipe selection (per subtask)

Pick a promoted `analysis_tools` candidate or skip to code generation.

## Output JSON

```json
{
  "tool_id": "uuid-or-null",
  "params": {"card_prefix": "E", "group_by": "STK_ID"},
  "rationale": "short",
  "use_none": false
}
```

- `use_none: true` when no candidate fits — pipeline generates pandas step.
- Merge params with brief filters; do not drop required filters.
- Prefer higher `score` when missing_aspects are non-critical (e.g. missing month label but trend recipe exists).
