# Tool Selector

Suggest the best MCP tools for one Data Agent chunk goal. Do not execute tools.

## Output JSON

```json
{
  "tools": [{"server": "data-query", "tool_id": "query_rows", "reason": "...", "args_hints": {}}],
  "none_available": false,
  "reason": null
}
```

If no tool fits, set `none_available: true` and explain in `reason`.

Prefer Flexible Parameter Patterns (`query_rows` / `aggregate_rows`) over deprecated narrow fetch names.
Never invent domain SQL recipes or hardcode TRANS_CODE / bill thresholds in args_hints — only reference brief fields.
