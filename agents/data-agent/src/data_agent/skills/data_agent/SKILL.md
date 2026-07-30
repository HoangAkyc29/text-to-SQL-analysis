# Data Agent

Solve supermarket analysis briefs by adaptive chunks. Ask Tool-Selector for tools each chunk. Never write SQL.

## Hard rules

1. Do not lock a fixed stage path up front — replan from observations.
2. Prefer resolve_products then query_rows with filters from brief values.
3. Fact tables need time_range. Do not invent TRANS_CODE filters.
4. Bill value thresholds from the brief belong on header amount sugar (`min_amount`), not invented line-only sums.
5. Prefer exports that keep columns needed for the brief; do not invent display-name filters to "prove" product type.
6. Coverage is structural (artifact readable, top-N counts, catalog-vs-bills) — grain column lists live in `data_dictionary/analysis_grain.yaml`, not in this skill.
7. Top-N **per product/SKU** → use `top_n_per_group` with a group key; export the
   frame you chose **before** finalize. Do not globally `limit_rows(top_n)` a
   correct per-group result.
8. Use confirmed `domain_rules_excerpt` and retrieved case `tool_chain` hints when
   they match the brief (parameterize from brief values). Relationships and
   ranking grain live in dictionary / Mongo facts — not hardcoded SQL here.
