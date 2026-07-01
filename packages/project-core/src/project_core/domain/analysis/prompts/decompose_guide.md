# LLM brief decomposition (pipeline)

Split `AnalysisBrief.intent` into `AnalysisPlan.subtasks` when the user asks for multiple analytic aspects (VIP + inventory, Q1 vs Q2, store + trend, …).

## Output JSON

```json
{
  "is_decomposed": true,
  "subtasks": [
    {
      "id": "st-vip-0",
      "intent": "focus clause for this aspect",
      "metrics": ["revenue"],
      "dimensions": ["STK_ID"],
      "filters": {}
    }
  ]
}
```

Rules:
- Single simple question → `is_decomposed: false`, one subtask mirroring brief.
- Preserve `filters` and `time_range` from parent brief on each subtask.
- Use Vietnamese intent clauses when user writes in Vietnamese.
- Do not invent SQL table names — only analytic focus strings.
