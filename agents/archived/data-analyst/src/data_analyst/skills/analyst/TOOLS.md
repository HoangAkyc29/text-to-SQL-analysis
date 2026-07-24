# Agent IV / Data Agent — tools

## Data Agent v2 fetch tools (no SQL from LLM)

When `DATA_AGENT_V2=1`, the pipeline runs `DataFetchToolkit` in-process. Decisions use `decision=fetch` with `tool_id`:

| tool_id | Purpose |
|---------|---------|
| `resolve_products` | SKU_DEF lookup before sale-line fetch |
| `preview_table` | TOP-N inspect (facts require `time_range`, limit ≤50) |
| `fetch_sale_lines` | STRANS lines for resolved `sku_ids` + time |
| `fetch_bill_headers` | TRANSHDR by time / `trans_nums` / `min_amount` |
| `fetch_lines_for_bills` | All lines for given `TRANS_NUM`s |
| `aggregate_metric` | Controlled server-side aggregates |
| `lookup_codes` | Distinct/sample code values (do not invent TRANS_CODE) |

SQL is built only inside handlers; agent payloads omit SQL strings. See `prompts/data_agent_guide.md`.

## Working set (catalog ops)

- Seed datasets: `q0`, `q1`, … from SQL parquet (legacy IV) **or** `save_as` refs from fetch tools (Data Agent).
- Transform ops take `dataset` + optional `save_as` to create a new named frame.
- Export/plot ops write under the trace `out/` directory and register artifacts.

## Core ops

| op_id | Purpose |
|-------|---------|
| `list_datasets` | Profile all datasets |
| `describe_columns` | null%, nunique, min/max / top values |
| `head_rows` / `sample_rows` | Preview rows |
| `value_counts` / `null_report` | Distributions / nulls |
| `assert_nonempty` / `assert_columns_present` | Critic checks |
| `select_columns` / `rename_columns` / `drop_columns` | Shape |
| `cast_column` / `add_column_expr` / `fill_null` / `drop_null` | Column ops (DSL expr, no free Python) |
| `filter_rows` | eq, ne, in, gt/gte/lt/lte, between, contains, startswith, endswith, regex, is_null… Args: `clauses`/`conditions`: `[{column, op|operator, value}]` or shorthand `column`+`op`+`value` |
| `sort_rows` / `limit_rows` / `distinct_rows` | Order / slice |
| `groupby_agg` | sum, mean, count, nunique, min, max, median, std |
| `pivot_table` / `melt` | Reshape |
| `window_rank` / `top_n_per_group` | Ranking |
| `percent_of_total` / `cumulative_sum` | Derived metrics |
| `join_datasets` / `concat_datasets` / `set_compare` | Multi-dataset |
| `export_csv` / `export_excel` / `plot_chart` | Deliverables (must write files) |
| `bundle_deliverables` | Mark primary artifacts |
| `match_brief_coverage` / `detect_empty_after_filter` / `grain_check` | Critic |

## Capability

Workflow grant: `tool:analysis-ops:run_analysis_op` (covered by `tool:*` in role configs). Data Agent also needs `execute_readonly` (see `AGENT_TOOLS["DATA"]`).
