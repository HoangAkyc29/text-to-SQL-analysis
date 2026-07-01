# Recipe selection & staging

Used by `recipe_selector` (LLM) and `execution_composer` (pipeline).

## Candidate shape

```json
{
  "tool_id": "uuid",
  "name": "vip_revenue_by_store",
  "score": 0.78,
  "matched_aspects": ["vip", "store"],
  "missing_aspects": ["month"],
  "param_schema": [{"name": "card_prefix", "type": "string"}]
}
```

## Selection rules

1. Prefer promoted recipe when `score >= 0.35` and missing aspects are non-blocking.
2. Merge `resolve_params(brief, subtask)` with LLM overrides.
3. If no candidate fits → generate pandas step; stage to `analysis_tools` after run.

## Staging

After `partial` or `complete` with `new_steps`:
- `AnalysisToolRegistry.stage_step` — per generated step
- `stage_from_run` — full multi-step script
- Dedup via `find_similar_intent` embedding + token hybrid

## MCP dynamic tools

Promoted recipes expose as `recipe_{name}` via `SandboxToolProvider` when Mongo registry is wired (`recipe_runtime.set_registry`).

## Script template patterns

Reuse recipes should:
- Read `path` as parquet/csv
- Write artifacts under `out / '{subtask_id}_summary.csv'`
- Use `params['group_by']` for dimensions
- Filter VIP: `df[df['CARD_NO'].astype(str).str.startswith(params['card_prefix'])]`

Generated fallback when no recipe:

```python
df = pd.read_parquet(path)
# groupby AMOUNT or metric from params
agg.to_csv(out / 'summary.csv')
```
