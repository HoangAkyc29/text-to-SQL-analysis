# Verified catalog-recipe selection

Recipes are reusable catalog-op chains. Free-form scripts and SQL are not
recipe steps.

## Candidate shape

```json
{
  "tool_id": "uuid",
  "name": "descriptive_recipe_name",
  "score": 0.78,
  "matched_aspects": ["requested_aspect"],
  "missing_aspects": [],
  "dataset_contracts": [{"role": "primary", "required_columns": ["<column>"]}],
  "dataset_bindings": {"primary": "q0"},
  "compatibility_status": "compatible",
  "verification_contract": {
    "source_run_verified": true,
    "replay_verified": true
  },
  "steps": [{"op_id": "<catalog op>", "args": {}}]
}
```

## Selection rules

1. Consider only promoted recipe-v2 candidates marked `compatible`.
2. Require permission, operation availability, dataset-role binding and schema
   preflight before execution.
3. Reuse the full compatible chain or prefix; generate missing catalog ops
   through the normal planner path.
4. Do not execute a candidate listed with rejection reasons.

## Staging

Runtime stages the canonical successful op chain, including export and
validation semantics. Promotion requires:

- verified source run;
- deterministic replay on compatible bound datasets;
- valid primary artifacts and required verification ops.

User feedback can change confidence but cannot bypass these gates.

## Parameters and bindings

- Dataset references use validated role bindings.
- Runtime values use declared parameter templates.
- Intermediate outputs may be referenced only after their producing step.
- A failed preflight step is regenerated through catalog planning; never repair
  it with source code.

## Knowledge boundary

Recipes describe data-processing operations. Domain definitions and formulas
belong in dictionary/RAG facts, while SQL case studies remain Agent II context.
Never copy a domain-specific SQL/filter recipe into this guide.
