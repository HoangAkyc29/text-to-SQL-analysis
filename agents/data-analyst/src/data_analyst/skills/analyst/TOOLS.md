# Agent IV — Analysis ops catalog (pipeline)

**Agent IV `decide()` returns JSON;** the IV brain executes **parameterized ops** in-process via `project_core.domain.analysis.ops` on parquet working sets.

Sandbox MCP (`run_analysis_script`) is **out of workflow** — kept in repo for debug only. Do not ask the LLM to write pandas scripts.

## Working set

- Seed datasets: `q0`, `q1`, … from SQL parquet paths.
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
| `filter_rows` | eq, ne, in, gt/gte/lt/lte, between, contains, startswith, endswith, regex, is_null… |
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

Workflow grant: `tool:analysis-ops:run_analysis_op` (covered by `tool:*` in role configs).
