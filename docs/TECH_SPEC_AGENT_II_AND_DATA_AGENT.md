# Đặc tả kỹ thuật: Data Agent + Tool-Selector (MCP redesign)

> Cập nhật 2026-07-24 — kiến trúc **MCP stdio + Tool-Selector**.  
> Agent II/III/IV (`sql-planner`, `risk-reviewer`, `data-analyst`) đã archive tại `agents/archived/`.  
> Tài liệu dài cũ về classic Agent II vẫn có thể tham khảo lịch sử; **path production** là Data Agent HTTP.

---

## 0. Topology hiện tại

```
Agent I (router) → chat-gateway pipeline
  → DATA_AGENT_V2=1 → invoke("DATA") HTTP data-agent:18206
       → mỗi chunk: HTTP tool-selector:18205
       → shortlist MCP tools (product-lookup | data-query | dataframe-ops | deliverables)
       → evidence → replan / finalize
  → sql-gateway HTTP chỉ nội bộ (builders / PolicyEngine), agent không gọi sql_* tools
```

| Thành phần | Port / path | Vai trò |
|------------|-------------|---------|
| `tool-selector` | 18205 `/run` | Gợi ý tool từ catalog + `mcp-servers/*/skills/*.md`; **không execute** |
| `data-agent` | 18206 `/run` | Adaptive chunks; gọi selector; execute fetch/ops |
| `mcp-servers/product-lookup` | stdio | `resolve_products` |
| `mcp-servers/data-query` | stdio | `preview_table`, `query_rows`, `aggregate_rows`, `lookup_distinct` |
| `mcp-servers/dataframe-ops` | stdio | transform / inspect ops |
| `mcp-servers/deliverables` | stdio | export / plot / validate |
| Classic II/III/IV | compose profile `classic-agents` | Archive only |

Flag: `DATA_AGENT_V2=1` trên gateway + analysis-worker (compose). Pipeline `_run_data_agent_v2` gọi `agent_invoker.invoke("DATA", …)` — không còn `run_data_agent_brain` in-process trên path chính.

---

## 1. Flexible fetch (không SQL từ LLM)

| Tool | Args chính |
|------|------------|
| `resolve_products` | `codes`, `limit` |
| `preview_table` | `table`, `time_range?`, `limit≤50` |
| `query_rows` | `table`, `filters[]`, `time_range` (bắt buộc fact), `order_by`, `limit`, `save_as`, `target_db` |
| `aggregate_rows` | như trên + `group_by`, `aggs[{fn,column}]` |
| `lookup_distinct` | `table`, `column`, `time_range?`, `contains?` |

**Cấm:** `raw_sql`, domain recipes trong skill (`TRANS_CODE='113'`, ngưỡng bill cứng).  
Sugar server-side: `sku_ids`, `trans_nums`, `min_amount`, `store_ids` → biên dịch thành `filters[]`.

Working set qua biên MCP: parquet dưới `DATA_AGENT_WORK_DIR` (`disk_ws` / dataset refs).

---

## 2. Adaptive loop (không stage cứng)

1. Data Agent băm **một** `chunk_goal` tiếp theo (LLM hoặc stub).
2. Gửi Tool-Selector: `{chunk_goal, brief_slice, available_datasets, prior_observations_summary, case_hints}`.
3. Selector trả `{tools:[{server,tool_id,reason,args_hints}], none_available?}`.
4. Data Agent execute shortlist (≤3), ghi observation + `stages` trail.
5. Replan / finalize khi đủ evidence hoặc hết `max_planner_turns`.

`case_hints` từ retrieve: `text`, `links`, `tool_chain`, `stages` — **gợi ý**, không ép path.

---

## 3. Case study redesign

| Field | Ý nghĩa |
|-------|---------|
| `stages` | Trail sau chạy (kể cả pivot) |
| `tool_chain` | `{server, tool_id\|op_id, args, save_as}` — dùng `query_rows`, không `fetch_sale_lines` |
| `sql_template` | Deprecated `[]` trên path Data Agent |
| `links` | Extract từ `table`/columns trong args hoặc SQL legacy |
| `kind` | `data_agent_chain` khi có tool_chain |

Seeds: `scripts/seed_gift_bill_case_study.py`, `scripts/seed_domain_rules_case_studies.py`.

---

## 4. Trial / integration path

```bash
# Unit (flexible fetch + acceptance stub brain)
uv run pytest packages/project-test/unit/project_core/test_data_fetch_toolkit.py \
  packages/project-test/unit/project_core/test_data_agent_acceptance.py \
  packages/project-test/unit/project_core/test_data_agent_audit_logging.py -q

# Compose (DATA_AGENT_V2=1)
docker compose up -d redis mongodb sql-gateway conversational-router tool-selector data-agent chat-gateway analysis-worker

# Seed case studies (cần embedding + Mongo)
uv run python scripts/seed_gift_bill_case_study.py
uv run python scripts/seed_domain_rules_case_studies.py

# Inspect trial
uv run python scripts/inspect_data_agent_trial.py <analysis_id>
```

Expect blob flags: `has_query_rows`, `has_resolve_products`, `has_data_agent_turn`, `has_tool_selector_suggest`, `audit_excerpt_count > 0`; không `TRANS_CODE='113'` từ skill; không Agent II `plan_sql` trên V2 path.

### Audit (logging kín)

| Event | Ai ghi | Nội dung |
|-------|--------|----------|
| `data_agent_turn` | data-agent | mỗi chunk / select / execute: tool_id, ok, error, args_preview, selector_tool_ids |
| `tool_selector_suggest` | tool-selector | chunk_goal → tools + args_hints |
| `data_agent_summary` | pipeline | stages, tool_chain, coverage, fetch counts |
| `workflow_timing` | pipeline | span timings |

`audit.jsonl` dùng chung volume `supermarket-state` (gateway + worker + data-agent + tool-selector). `/analyses/{id}/trial-log` khớp theo `trace_id` / `analysis_id`.

---

## 5. Archive

Xem `agents/archived/ARCHIVED.txt`. Compose services II/III/IV dưới `profiles: ["classic-agents"]`.

---

*Phần atlas / Agent II chi tiết bên dưới có thể lệch so với redesign; ưu tiên §0–§4 khi vận hành.*

---
