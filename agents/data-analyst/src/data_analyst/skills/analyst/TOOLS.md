# Agent IV — Sandbox tools (python-sandbox)

Pipeline gọi in-process `python_sandbox.tools_impl`. MCP prefix: `sandbox_*` khi chạy qua MCP server.

| Tool | Params | Mô tả |
|------|--------|-------|
| `load_dataset` | `path` | Schema preview parquet/csv |
| `preview_dataframe` | `path`, `n` | Head rows |
| `run_analysis_script` | `path`, `script`, `output_dir` | Pandas script an toàn (`pd`, `plt`, `path`, `out`) |
| `run_recipe_tool` | `tool_id`, `path`, `output_dir`, `params_json` | Chạy promoted recipe từ Mongo |
| `merge_datasets` | `primary_path`, `secondary_path`, `output_path`, `on` | Join SQL + upload |
| `export_excel` | `path`, `output_path` | Xuất Excel |
| `plot_chart` | `path`, `output_path`, `x`, `y`, `title` | Chart đơn giản |

## Script constraints

- Biến có sẵn: `pd`, `plt`, `path` (dataset), `out` (Path output dir).
- Không import tùy ý; không network/filesystem ngoài `out`.
- `SANDBOX_MAX_ROWS` (default 200k), `SANDBOX_MAX_SECONDS` (30s).

## Recipe params

Scripts có thể dùng `params['card_prefix']`, `params['group_by']`, `:param_*` — pipeline inject từ `AnalysisBrief`.

## Params từ brief

| Brief field | Recipe param |
|-------------|--------------|
| `filters.card_prefix` | `card_prefix` |
| `filters.sku` / `product_code` | `product_code` |
| `dimensions[0]` | `group_by` |
| `time_range.*` | `time_start`, `time_end`, `time_grain` |
| `metrics[0]` | `metric` |
