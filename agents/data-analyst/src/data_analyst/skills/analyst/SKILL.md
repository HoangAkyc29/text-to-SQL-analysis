# Agent IV — Data Analyst

Thực thi phân tích trên dataset parquet từ sql-gateway bằng **catalog ops** tham số hóa (không codegen sandbox trong workflow).

## Runtime

- LLM brain: `project_core.domain.analysis.iv_brain.run_analysis_brain` + `reason_loop_guide`
- Fallback deterministic: `iv_analyzer.analyze_datasets` (chuỗi ops cố định)
- Ops: `project_core.domain.analysis.ops`

Pipeline truyền: `brief`, `dataset_manifest`, `result_profile`, `recipe_candidates` (op_chain), semantics.

## Actions

| `action` | Ý nghĩa |
|----------|---------|
| `complete` | Đủ coverage, có artifacts |
| `partial` | Thiếu format / một phần — vẫn trả kết quả |
| `data_feedback` | Cần Agent II chạy lại SQL |
| `suggest_clarify` | Exploration / làm rõ với user |

## Composable execution

1. Working set `q0`, `q1`, … từ parquet.
2. Mỗi bước: `run_op` với `op_id` + args (+ `save_as`).
3. Export CSV/Excel/chart bắt buộc trước finalize.
4. Stage recipe dưới dạng **op_chain** (không script).

Sandbox `run_analysis_script` giữ trong package MCP nhưng **không thuộc workflow**.

## Đọc thêm

- `TOOLS.md` — catalog ops
- `prompts/reason_loop_guide.md`
- `prompts/analyze_guide.md`
