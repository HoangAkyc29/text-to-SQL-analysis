# Agent IV — Data Analyst

Thực thi phân tích trên dataset parquet từ sql-gateway, merge upload ngoài, chạy recipe composable, và báo cáo kết quả / data feedback.

## Runtime

Implementation: `project_core.domain.analysis.iv_analyzer.analyze_datasets` (in-process pandas sandbox).

Pipeline truyền:
- `brief`, `dataset_manifest`, `result_profile`
- `analysis_plan`, `execution_plan`, `recipe_candidates`
- `analysis_tools` (promoted recipes)
- `domain_rules_excerpt`

## Actions

| `action` | Ý nghĩa |
|----------|---------|
| `complete` | Đủ coverage, có artifacts |
| `partial` | Một phần reuse recipe, một phần generated — vẫn trả kết quả |
| `data_feedback` | Cần Agent II chạy lại SQL (empty, mismatch SKU, grain) |
| `suggest_clarify` | Exploration mode — gợi ý làm rõ với user |

## Composable execution

1. `execution_plan` từ pipeline (ưu tiên) hoặc build từ candidates.
2. Mỗi step: `run_analysis_script` hoặc `run_recipe_tool(tool_id)`.
3. Stage generated steps → Mongo `analysis_tools`.

## External data

- `brief.external_sources[].parquet_path` merged với SQL dataset qua `merge_datasets`.
- Join key ưu tiên: `SKU`, `BARCODE`, `STK_ID`.

## Đọc thêm

- `prompts/analyze_guide.md`
- `prompts/recipe_guide.md`
