# Probe & data feedback

## `probe_sql` action

When `inbox.probe_mode` or `inbox.data_feedback.probe_requests` is set:

```json
{
  "action": "probe_sql",
  "sql_queries": ["SELECT TOP 100 ...", "..."],
  "query_meta": [{"role": "probe", "purpose": "resolve_identifier", "requirement_ids": ["filter:0"]}, "..."],
  "target_dbs": ["db2", "db2"],
  "reasoning": "IV-requested probes"
}
```

Probe SQL should be **small** (`TOP 100`–`1000`), read-only, aimed at resolving ambiguity.

## Common `data_feedback.issue` values

| Issue | Planner response |
|-------|------------------|
| `empty_result` | Re-check current brief constraints against dictionary, samples, and prior observations |
| `identifier_mismatch` | Probe the dictionary-selected identifier source and use its resolved key |
| `probe_success_needs_fact` | Stop probing and emit a `role: main` query grounded in selected table metadata |
| `grain` | Re-plan at the grain documented by dictionary and samples |
| `needs_sql_retry` | Adjust filters per `suggested_intent_fix` |

## `inbox.db_error_feedback` (execute failed)

When present, SQL passed policy/review but the engine rejected it:

```json
{
  "error": "db_error",
  "message": "Invalid column name 'TRAN_TIME'.",
  "rejected_sql": "WITH …",
  "target_db": "db2",
  "hints": ["…"]
}
```

Fix the **engine** issue (missing CTE columns, bad object name, syntax). Prefer splitting into simpler queries. Do **not** invent domain SQL recipes from hints.

## Exploration mode

When `brief.exploration_mode` or `user_knowledge_level: unknown`:
- Emit only the smallest probes needed to resolve the named uncertainty.
- Derive every probe table, column, and value shape from selected dictionary entries and `inbox.table_samples`.
- Mark `query_meta[].purpose` and `query_meta[].requirement_ids` clearly.

## Requirement coverage

For every query, copy the requirement IDs it serves from `brief.requirements`.
Do not infer a fixed master table, fact table, join, document code, or predicate from the requirement name alone.
