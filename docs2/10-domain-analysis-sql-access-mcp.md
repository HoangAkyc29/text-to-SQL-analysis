# Domain: analysis, access, SQL, MCP (Phần AB)

Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) (dòng 14259–16758).

← [Mục lục docs2](README.md)

---

# Phần AB — Domain Analysis, Access, SQL và MCP (từ mã nguồn)

*Mô tả chi tiết bằng tiếng Việt các module: `project_core/domain/analysis/*`, `project_core/domain/access/*`, `project_core/domain/sql/*`, `sql_gateway/tools_impl.py`, `python_sandbox/tools_impl.py`, `runner_child.py`.*

---

## §AB.0 — Kiến trúc tổng thể ba lớp domain

Ba lớp domain bổ sung cho pipeline đã mô tả ở §Z.2:

| Lớp | Thư mục | Vai trò |
|-----|---------|---------|
| Phân tích | `domain/analysis/` | Brief → plan → recipe → sandbox IV |
| Truy cập | `domain/access/` | Claims, capability, context agent |
| SQL | `domain/sql/` | Policy, shard, parameterize, profile |
| MCP thực thi | `sql-gateway`, `python-sandbox` | Cổng ODBC và sandbox pandas |

Luồng dữ liệu quyền: JWT/user dict → `claims_from_user_dict` → `build_permissions_snapshot` → `PermissionsSnapshot` → `ContextPolicy` / `PolicyEngine` / `grant_denial` trên MCP.

---

## §AB.1 — `iv_analyzer.py` (Orchestrator Agent IV)

**Đường dẫn:** `packages/project-core/src/project_core/domain/analysis/iv_analyzer.py`

**Logger:** `project_core.domain.analysis.iv_analyzer`

### AB.1.1 — Import và lazy sandbox

Hàm `_sandbox()` thực hiện import lazy `from python_sandbox import tools_impl` — tránh import vòng lúc load project-core và cho phép chạy in-process trong monorepo (không bắt buộc MCP HTTP).

**Các import contract:** `AnalysisPlan`, `ExecutionCoverage`, `ExecutionStepPlan`, `RecipeCandidate`, `RecipeStep`, `AnalysisBrief`, `ClarificationRequest`, `DataFeedback`, `ExpectedVsObserved`, `ProbeRequest`.

**Import nội bộ:** `build_execution_plan`, `rank_candidates`, `decompose_brief`, `apply_params_to_script` (từ feedback registry).

### AB.1.2 — `analyze_datasets` — chữ ký đầy đủ

```text
analyze_datasets(
    *,
    brief: AnalysisBrief,
    manifest: dict[str, Any],
    profile: dict[str, Any],
    out_dir: str,
    max_steps: int = 8,
    query_meta: list[dict[str, Any]] | None = None,
    analysis_tools: list[dict[str, Any]] | None = None,
    recipe_candidates: list[dict[str, Any]] | None = None,
    analysis_plan: AnalysisPlan | dict[str, Any] | None = None,
    execution_plan: list[dict[str, Any]] | None = None,
    domain_rules_excerpt: str = "",
) -> dict[str, Any]
```

**Lưu ý:** `domain_rules_excerpt` nhận vào nhưng không được đọc trong thân hàm hiện tại — placeholder cho mở rộng prompt/rules.

### AB.1.3 — Giai đoạn 1: Thu thập path và phân loại probe

1. `paths = [q.get("path") for q in manifest.get("queries", []) if q.get("path")]` — bỏ query không có path.
2. `paths, meta = _merge_external_paths(brief, paths, query_meta or [])` — nối file upload user.
3. `row_counts = {i: int(q.get("row_count", 0)) for i, q in enumerate(manifest.get("queries", []))}`.
4. `probe_idxs`: index meta có `role == "probe"`.
5. `main_idxs`: role khác probe; nếu rỗng → `list(range(len(paths)))` (coi tất cả là main).
6. `main_rows`, `probe_rows` = tổng row_count theo nhóm index.
7. `product_code` từ `brief.filters` key `product_code` hoặc `sku`.

**Early return identifier_mismatch:** Điều kiện đồng thời `main_rows == 0`, `probe_rows > 0`, `product_code` truthy → `_identifier_mismatch_feedback`.

**Early return empty profile:** `profile.get("row_count", 0) == 0` → `_empty_feedback`.

### AB.1.4 — Giai đoạn 2: Plan và merge dataset

`plan = _coerce_plan(analysis_plan, brief)`:
- `None` + `brief.plan` → dùng brief.plan
- `None` không plan → `decompose_brief(brief)`
- `dict` → `AnalysisPlan.model_validate`
- else giữ object

**Merge SQL + external:** Tách `external_paths` (meta role external) và `sql_paths` (khác external). Nếu cả hai có file tồn tại:
- `merged_out = out_dir / "merged_upload.parquet"`
- `sandbox.merge_datasets(sql_paths[0], external_paths[0], merged_out)`
- status ok → prepend path merged và meta `{"role": "merged", "join_key": ...}`
- Exception → log warning, tiếp tục không merge

### AB.1.5 — Giai đoạn 3: `_resolve_execution`

**Nếu `execution_plan` có giá trị:**
- Validate từng dict → `ExecutionStepPlan`
- `ExecutionCoverage(diagnosis="partial" if steps else "none")`
- **Không** gọi matcher/composer — pipeline đã quyết định trước (xem §Z.2.6.19 `build_execution_plan`).

**Else:** Với mỗi `subtask` trong `plan.subtasks`:
- Nếu `recipe_candidates` và phần tử đầu có `subtask_id`: lọc candidate cùng id, validate bỏ key `subtask_id`
- Else: `rank_candidates(subtask.intent, analysis_tools or [], top_k=5)`
- Gán `candidates_by_subtask[subtask.id]`

Gọi `build_execution_plan(plan, dataset_paths=paths, query_meta=meta, candidates_by_subtask=..., brief=brief)`.

### AB.1.6 — Giai đoạn 4: Preview và vòng exec_steps

**Biến theo dõi:** `steps_run = 0`, `artifacts: list[str]`, `metrics` khởi tạo `row_count` từ profile, `new_steps: list[RecipeStep]`.

**Preview (tối đa 2 path đầu):**
- Điều kiện: `steps_run < max_steps`, path tồn tại
- `sandbox.preview_dataframe(path, n=30)`
- Tăng steps_run; nếu không có key `error`, ghi `metrics[f"preview_rows_{steps_run}"] = len(preview)`

**Vòng `for exec_step in exec_steps`:**
1. Vượt max_steps → append gap `budget_exceeded:{subtask_id}`, break
2. `dpath = exec_step.dataset_path or paths[0]` — thiếu file → gap `missing_dataset`
3. `sub_out = Path(out_dir) / exec_step.subtask_id`, mkdir
4. `script = apply_params_to_script(step.script_template, step.params)`
5. `sandbox.run_analysis_script(dpath, script, sub_out)` — không truyền tool_grants (in-process tin cậy)
6. ok → extend artifacts; `step.status == "generated"` → append new_steps
7. Exception → log warning, gap `step_failed:{step_id}`

### AB.1.7 — Giai đoạn 5: Chart, exploration, impossible

**Chart:** `"chart" in (brief.output_format or [])`, còn budget, path[0] tồn tại:
- `_column_names(primary)` — cần ≥2 cột
- `plot_chart(primary, chart_path, cols[0], cols[1], title=brief.intent[:80])`

**Exploration clarify:** `brief.exploration_mode` và `main_rows > 0` và còn budget → `_exploration_clarify`; nếu trả dict → return ngay (action suggest_clarify).

**Impossible:** `_is_impossible_analysis(...)` → payload action impossible, reason metric_not_mappable.

### AB.1.8 — Payload kết thúc

| Khóa | Nguồn |
|------|-------|
| `action` | `complete` hoặc `partial` nếu coverage.diagnosis == partial |
| `headline_metrics` | metrics dict |
| `artifact_paths` | artifacts list |
| `caveats` | coverage.gaps[:5] |
| `sandbox_steps` | steps_run |
| `coverage` | coverage.model_dump() |
| `new_steps` | serialized RecipeStep generated |
| `analysis_script` | new_steps[0].script_template nếu có new_steps |

### AB.1.9 — `_coerce_plan`

Đã mô tả AB.1.4 — điểm vào thống nhất plan từ pipeline hoặc decompose on-demand.

### AB.1.10 — `_merge_external_paths`

Duyệt `brief.external_sources or []`:
- `pp = ext.parquet_path or ext.path`
- Nếu `pp` và `Path(pp).exists()`:
  - append path
  - meta append `{role: external, file_id, source: original_name, row_count}`

Không validate `ExternalSource` model tại đây — giả định brief đã validate upstream.

### AB.1.11 — `_column_names(path)`

Try read parquet nếu suffix `.parquet` else csv. Return `list(df.columns.astype(str))`. Exception → log warning, `[]`.

### AB.1.12 — `_is_impossible_analysis` — logic đầy đủ

**Return False ngay nếu `main_rows <= 0`** — không kết luận impossible khi không có dữ liệu main (đã xử lý ở feedback trước).

**Nhánh metric không map:** `coverage.diagnosis == "none"` AND `steps_run == 0` AND `brief.metrics` non-empty:
- Lấy primary path đầu tiên truthy
- `cols = {c.lower() for c in _column_names(primary)}`
- Với mỗi metric: nếu `metric.lower() not in cols` và không thuộc `{"revenue", "amount", "points"}` → return True

**Nhánh tích cực:** `steps_run >= 1` và diagnosis none và không gaps → return False (đã chạy được gì đó).

**Nhánh budget:** `budget_exceeded` gaps và `steps_run >= 1` và không path truthy → True.

Default return False.

### AB.1.13 — `_identifier_mismatch_feedback`

Tạo `observed` string từ probe row counts. Return dict:
- `action: data_feedback`
- `data_feedback`: DataFeedback model_dump với needs_sql_retry, issue identifier_mismatch, diagnosis needs_user_clarify
- `suggest_clarify`: `_product_clarify(product_code).model_dump()`

### AB.1.14 — `_empty_feedback`

Nếu có product_code → hai `ProbeRequest` (SKU_DEF, BARCODE) với LIKE pattern (SQL nhúng trực tiếp product_code — rủi ro injection nếu code không sanitize upstream).

Return action data_feedback, diagnosis needs_probe hoặc solvable.

### AB.1.15 — `_product_clarify` và `_exploration_clarify`

**Product:** ClarificationRequest tiếng Việt, reason product_code_ambiguous, 3 options barcode / sku_padded / unknown exploration.

**Exploration:** Chỉ khi `user_knowledge_level == "unknown"`. evidence_summary chứa JSON row_counts. Options revenue / trend / continue exploration.

### AB.1.16 — Callers của analyze_datasets

| Caller | Ngữ cảnh |
|--------|----------|
| `agents/data-analyst` service | mode analyze sau SQL execute |
| `SupermarketAnalysisPipeline` | invoke IV với payload đầy đủ |
| Unit test IV | mock manifest/profile |

---

## §AB.2 — `recipe_runtime.py`

**Đường dẫn:** `packages/project-core/src/project_core/domain/analysis/recipe_runtime.py`

**Toàn bộ module:** 18 dòng — global `_registry: AnalysisToolRegistry | None`.

| API | Mô tả |
|-----|-------|
| `set_registry(registry)` | Gán global; gọi lúc app startup khi wire Mongo/registry |
| `get_registry()` | Đọc global; `run_recipe_tool` trong sandbox dùng |

**TYPE_CHECKING:** Import `AnalysisToolRegistry` chỉ cho type hint — tránh import runtime nặng.

**Hành vi khi registry None:** MCP `run_recipe_tool` trả `{"error": "recipe_registry_unavailable", "tool_id": ...}`.

---

## §AB.3 — Tóm tắt chuỗi analysis đã đọc từ mã (cross-reference)

Các module `decomposer`, `param_resolver`, `recipe_matcher`, `recipe_retriever`, `recipe_selector`, `execution_composer` tạo chuỗi:

```text
decompose_brief → AnalysisPlan
rank_candidates / hybrid_rank_candidates → RecipeCandidate[]
select_recipe_for_subtask → (candidate, params)
build_execution_plan → ExecutionStepPlan[] + ExecutionCoverage
analyze_datasets → chạy sandbox + payload IV
```

**Ngưỡng điểm quan trọng trong mã nguồn:**

| Vị trí | Ngưỡng | Ý nghĩa |
|--------|--------|---------|
| recipe_matcher | score > 0.05 | Lọc candidate yếu |
| recipe_selector stub | score < 0.2 | Không chọn recipe |
| execution_composer | min_reuse_score 0.35 | Reuse không cần LLM chosen |
| iv_analyzer | max_steps 8 | Budget sandbox mặc định |

---

## §AC.0 — Domain Access (`project_core/domain/access/`)

Bốn tệp: `user_claims.py`, `acl.py`, `permission_set.py`, `context_policy.py`.

### AC.0.1 — Luồng từ JWT đến enforcement

```text
user dict (JWT claims)
  → claims_from_user_dict → (actor_id, role, store_ids)
  → build_permissions_snapshot → PermissionsSnapshot
  → ContextPolicy.can_invoke_tool / can_execute_sql / filter_schema_excerpt
  → PolicyEngine (SQL) / grant_denial (MCP)
```

---

## §AC.1 — `user_claims.py`

**Đường dẫn:** `packages/project-core/src/project_core/domain/access/user_claims.py`

### AC.1.1 — `normalize_store_ids(raw: Any) -> list[int] | None`

| Input | Output |
|-------|--------|
| `None` | `None` |
| `list` | int từng phần tử, bỏ None/""; rỗng → None |
| `str` | split comma, strip, int; rỗng → None |
| scalar khác | `[int(raw)]` |

**Mục đích:** Chuẩn hóa claim `store_ids` từ JWT hoặc session — dùng cho store filter SQL.

### AC.1.2 — `claims_from_user_dict(user: dict) -> tuple[str, str, list[int] | None]`

- `actor_id = str(user["sub"])` — **KeyError** nếu thiếu sub
- `role = str(user.get("role") or "hq_analyst")` — default role HQ
- `store_ids = normalize_store_ids(user.get("store_ids"))`

**Không validate role** tồn tại trong config — việc đó ở `build_permissions_snapshot` / DB.

---

## §AC.2 — `permission_set.py`

**Đường dẫn:** `packages/project-core/src/project_core/domain/access/permission_set.py`

**Docstring module:** Mô hình capability với namespace:
- `data:table:<NAME>` — quyền bảng; `data:table:*` = tất cả
- `data:column_deny:<COL>` — cấm cột
- `data:store_filter:required` — bắt buộc lọc cửa hàng
- `tool:<server>:<action>` — MCP; `tool:*` = tất cả
- `function:<tool_id>` — recipe sandbox; `function:*` = tất cả

Wildcard: segment `:*` tại ranh giới `:` — ví dụ `tool:sql-gateway:*`.

### AC.2.1 — Hằng số

| Hằng | Giá trị |
|------|---------|
| `CAP_DATA_TABLE` | `"data:table:"` |
| `CAP_DATA_COLUMN_DENY` | `"data:column_deny:"` |
| `CAP_DATA_STORE_FILTER` | `"data:store_filter:required"` |
| `CAP_TOOL_PREFIX` | `"tool:"` |
| `CAP_FUNCTION_PREFIX` | `"function:"` |

### AC.2.2 — `MCP_TOOL_CAPABILITY`

Ánh xạ tên tool MCP → capability canonical:

| Tool name | Capability |
|-----------|------------|
| validate_sql | tool:sql-gateway:validate |
| explain_sql | tool:sql-gateway:explain |
| get_schema_snapshot | tool:sql-gateway:explain |
| execute_readonly | tool:sql-gateway:execute |
| run_analysis_script | tool:python-sandbox:run_analysis_script |
| preview_dataframe | tool:python-sandbox:preview_dataframe |
| load_dataset | tool:python-sandbox:load_dataset |
| merge_datasets | tool:python-sandbox:merge_datasets |
| plot_chart | tool:python-sandbox:plot_chart |
| export_excel | tool:python-sandbox:export_excel |
| run_recipe_tool | tool:python-sandbox:run_recipe_tool |

`ALL_TOOL_CAPABILITIES`: tuple sorted unique values — role admin full tool.

### AC.2.3 — `AGENT_TOOLS`

| Agent key | Tuple tool names |
|-----------|------------------|
| II | validate_sql |
| III | explain_sql, get_schema_snapshot |
| IV | run_analysis_script, preview_dataframe, export_excel, plot_chart, load_dataset, merge_datasets |

**Nguồn sự thật duy nhất** cho tool agent được phép gọi — `ContextPolicy.allowed_mcp_tools` đọc từ đây.

**Lưu ý:** `run_recipe_tool` không trong AGENT_TOOLS IV — invoke qua registry riêng với `allowed_functions`.

### AC.2.4 — `capability_granted(grants, key) -> bool`

1. grants falsy → False (fail-closed)
2. Exact match key in grant_set → True
3. Wildcard: với mỗi i từ 1 đến len(parts)-1, kiểm `":".join(parts[:i]) + ":*"` in grant_set
4. Else False

**Ví dụ:** key `tool:sql-gateway:execute`, grants có `tool:sql-gateway:*` → True.

### AC.2.5 — `tool_capability_for(tool_name)`

Lookup `MCP_TOOL_CAPABILITY`; default `f"tool:{tool_name}"` nếu không có trong map.

### AC.2.6 — `grant_denial(grants, capability, violation)`

Nếu granted → None. Else dict:
```json
{"error": "policy_blocked", "status": "policy_blocked", "violations": [violation]}
```

Dùng chung sql-gateway và python-sandbox để shape deny đồng nhất.

### AC.2.7 — Dataclass `PermissionSet`

**Field:** `keys: frozenset[str]`

**`from_keys(keys)`:** Strip, bỏ rỗng, frozenset.

**`full_access()`:** frozenset `data:table:*`, `tool:*`, `function:*`.

**`_wants_all_tables()`:** `"data:table:*" in keys` hoặc `"data:*" in keys`.

**`to_snapshot(actor_id, role, store_ids, all_tables)`:**

- allowed_tables: nếu wants all → sorted unique all_tables; else extract từ keys `data:table:X` không kết thúc `:*`
- denied_columns: từ `data:column_deny:X`
- tool_grants: keys startswith `tool:`
- allowed_functions: keys startswith `function:`
- store_filter_required: `CAP_DATA_STORE_FILTER in keys`

Return `PermissionsSnapshot` Pydantic.

---

## §AC.3 — `acl.py`

**Đường dẫn:** `packages/project-core/src/project_core/domain/access/acl.py`

### AC.3.1 — `role_config(role, config=None)`

Load `ProjectConfig` (default `load_project_config()`), return `cfg.roles.get(role, RoleConfig())` — role lạ → config rỗng.

### AC.3.2 — `_default_all_tables()`

Lazy import `SchemaCatalog.from_dictionary_dir().logical_table_names()` — tránh import nặng lúc module load.

### AC.3.3 — `build_permissions_snapshot(...)`

**Hai đường:**

**A — Production DB (`permission_set` not None):**
- `tables = all_tables or _default_all_tables()`
- `permission_set.to_snapshot(actor_id, role, store_ids, tables)`

**B — Dev fallback (`ALLOW_DEV_AUTH` path trong docstring):**
- `rc = role_config(role)`
- `PermissionsSnapshot` trực tiếp từ yaml: allowed_tables, denied_columns, store_ids, store_filter_required, tool_grants, allowed_functions từ `RoleConfig`
- **Fail-closed:** role yaml thiếu tool_grants → list rỗng → deny

**Docstring nhấn mạnh:** Production phải truyền `permission_set` từ AUTH DB; dev đọc yaml verbatim.

---

## §AC.4 — `context_policy.py`

**Đường dẫn:** `packages/project-core/src/project_core/domain/access/context_policy.py`

**Class `ContextPolicy`** — không state instance; các method pure logic.

### AC.4.1 — `build_request_context(agent, actor_id, session, *, extra=None)`

Khởi `ctx = {agent, actor_id}`.

| agent | ctx bổ sung |
|-------|-------------|
| I | transcript, workflow_summary, clarification_request từ extra |
| II | brief dump, workflow steps dump, inbox = extra or {} |
| III | extra or {} |
| IV | extra or {} |

**`_workflow_summary(workflow)`:** status.value, active_analysis_id, last_outcome; None → {}.

### AC.4.2 — Tool permission helpers

| Method | Logic |
|--------|-------|
| `allowed_mcp_tools(agent)` | list(AGENT_TOOLS.get(agent, ())) |
| `is_tool_allowed(agent, tool)` | tool in allowed set |
| `can_invoke_tool(permissions, agent, tool)` | allowed AND capability_granted(tool_grants, tool_capability_for(tool)) |
| `can_execute_sql(permissions)` | capability_granted(..., "tool:sql-gateway:execute") |
| `can_invoke_function(permissions, function_id)` | capability_granted(allowed_functions, f"function:{function_id}") |

### AC.4.3 — `filter_schema_excerpt(snapshot, catalog_tables)`

`allowed = {t.lower() for t in snapshot.allowed_tables}` — filter dict catalog chỉ bảng được phép (case-insensitive key).

**Dùng bởi:** Agent III khi nhận schema context đã lọc theo role.

---

*§AC tiếp: domain/sql — §AD MCP sql-gateway — §AE python-sandbox*
---

## §Z.2.12 — Phụ lục bổ sung: ví dụ payload và kịch bản tích hợp (8 tệp §Z.2.1–Z.2.8)

*Phụ lục này bổ sung ví dụ cụ thể cho các tệp đã nêu ở §Z.2.1–§Z.2.8 — không lặp định nghĩa hàm đã mô tả.*

### §Z.2.12.1 — Ví dụ `AgentRequest` tới ConversationalRouterService (ingress)

Khi người dùng gửi «Cho tôi biểu đồ doanh thu VIP tháng trước», orchestrator gọi `HttpAgentInvoker.invoke("I", payload, metadata)` với metadata gần đúng:

```json
{
  "session_id": "sess-abc-123",
  "actor_id": "user-42",
  "mode": "ingress",
  "permissions": { "role": "hq_analyst", "capabilities": ["..."] }
}
```

Payload `{}` hoặc rỗng — vì `message` nằm trong `AgentRequest.message` dạng text thuần, không phải JSON payload II/IV.

`decide()` đọc `mode` từ metadata, gọi `_ingress`. LLM (hoặc stub) trả:

```json
{
  "route": "analysis",
  "user_message": "Tôi sẽ phân tích doanh thu VIP theo tháng.",
  "brief": {
    "intent": "doanh thu VIP tháng trước",
    "metrics": ["revenue"],
    "output_format": ["chart"],
    "filters": {}
  }
}
```

Orchestrator nhận `route=analysis` → khởi tạo `WorkflowState`, gọi pipeline với `brief` đã validate.

**Trường hợp biên ví dụ:** Tin nhắn `"{not json"` — `_ingress` bắt `JSONDecodeError`, dùng nguyên chuỗi làm text; không crash.

### §Z.2.12.2 — Ví dụ clarification_bridge sau POST `/chat/clarify`

User chọn option `prefix_e` cho câu hỏi `vip_card_prefix`. Body:

```json
{
  "session_id": "sess-abc-123",
  "reply": {
    "question_id": "vip_card_prefix",
    "option_id": "prefix_e"
  }
}
```

Orchestrator invoke Agent I với `mode=clarification_bridge`, metadata chứa `clarification_request` (bản gốc từ Agent II) và `transcript` các lượt trước.

`_clarification_bridge` trả brief cập nhật `filters.card_prefix = "E"` — pipeline tiếp tục mà không cần LLM clarify lại.

**Edge:** `transcript` thiếu lượt user mới nhất — heuristic stub có thể không map option → brief sai.

### §Z.2.12.3 — Ví dụ SqlPlannerService `action: clarify` (stub VIP)

Brief intent «Phân tích khách VIP mua nhiều nhất» lần `attempt=1`, không `card_prefix`, stub trả:

```json
{
  "action": "clarify",
  "clarification_request": {
    "reason": "missing_vip_definition",
    "partial_brief": { "...": "..." },
    "questions": [
      {
        "id": "vip_card_prefix",
        "prompt": "VIP được định nghĩa thế nào?",
        "options": [
          { "id": "prefix_e", "label": "Card bắt đầu E", "brief_value": { "filters": { "card_prefix": "E" } } }
        ]
      }
    ]
  }
}
```

Pipeline (qua orchestrator) chuyển sang `AWAITING_CLARIFICATION`, UI gọi `/chat/clarify`.

**Edge:** `attempt=2` với cùng brief — stub **không** hỏi lại VIP; đi thẳng nhánh SQL mặc định CSCARD+PMTRANS.

### §Z.2.12.4 — Ví dụ `plan_sql` với product_code

`brief.filters.product_code = "8934567890123"`. Stub gọi `resolve_product_code`:

- Probe SQL có thể thêm 1–2 câu lookup BARCODE/SKU_DEF.
- Main query GROUP BY SKU_ID trên STRANS TRANS_CODE 113.

Đầu ra gồm `query_meta` phân biệt `role: probe` vs `main`, `target_dbs` song song độ dài `sql_queries`.

**Edge:** `resolve_product_code` không tìm thấy candidate — predicate fallback `SKU_ID = '8934...'` vẫn chạy; III có thể approve nếu policy cho phép bảng STRANS.

### §Z.2.12.5 — Ví dụ RiskReviewerService reject policy

SQL đầu vào: `SELECT * FROM sys.tables`. `PolicyEngine.validate` trả `allowed=False`, violations chứa tên bảng hệ thống.

Nhánh không stub (dòng 74–89) trả ngay:

```json
{
  "verdict": "reject",
  "concerns": ["table_not_allowed:sys.tables"],
  "risk_feedback": {
    "issue": "table_not_allowed:sys.tables",
    "suggestion": "Fix SQL to use allowlisted tables and readonly SELECT only."
  },
  "schema_context_summary": { "table_count": 12, "has_domain_definitions": true }
}
```

LLM **không** được gọi — tiết kiệm token và đảm bảo deterministic deny.

**Edge stub:** Cùng SQL nhưng `ALLOW_LLM_STUB=1` — vẫn reject nếu policy deny; thêm scan `drop/delete/...` trên chuỗi SQL.

### §Z.2.12.6 — Ví dụ RiskReviewerService approve + LLM semantic

SQL hợp lệ policy: `SELECT TOP 100 STK_ID, SUM(AMOUNT) FROM STRANS WHERE TRANS_CODE='113' GROUP BY STK_ID`.

`verdict.allowed=True`, không stub → LLM `review_guide` nhận full ACL + `schema_context`. Model có thể trả `verdict: approve` hoặc `reject` nếu phát hiện full scan nguy cơ — `needs_explain` có thể true ở stub khi concern chứa «scan».

**Edge:** LLM reject nhưng policy approve — pipeline phải tôn trọng `verdict` từ JSON LLM (hành vi orchestrator/pipeline, không phải service III).

### §Z.2.12.7 — Ví dụ DataAnalystService `tool_not_granted`

`PermissionsSnapshot` thiếu capability `run_analysis_script` cho agent IV:

```json
{
  "action": "data_feedback",
  "data_feedback": {
    "needs_sql_retry": false,
    "issue": "tool_not_granted",
    "summary": "run_analysis_script not granted",
    "diagnosis": "impossible"
  },
  "impossible_reason": "tool_not_granted:python-sandbox:run_analysis_script"
}
```

Không raise exception — pipeline nhận `impossible` outcome thay vì crash gateway.

**Edge:** Một phần `recipe_candidates` có `tool_id` không được phép — bị lọc trước `analyze_datasets`; IV có thể chạy với subset recipe.

### §Z.2.12.8 — Ví dụ luồng `POST /auth/login` → `POST /chat`

1. Client `POST /auth/login` `{"username":"analyst1","password":"***"}`.
2. `authenticate` query AUTH DB → `AuthUser`.
3. `issue_token` → JWT 8 giờ, `store_ids` normalized.
4. Client `POST /chat` header `Authorization: Bearer <jwt>`.
5. `current_user` decode → `sub`, `role`, `store_ids`.
6. `handle_chat` load permissions qua `load_effective_permissions(sub)` (orchestrator).
7. `invoke("I")` với permissions trong metadata agent.

**Edge dev:** Bỏ bước 1–3, set `ALLOW_DEV_AUTH=1` → `current_user` trả dev-user không cần header.

### §Z.2.12.9 — Ví dụ `HttpAgentInvoker.invoke` metadata cho Agent II

```json
{
  "session_id": "sess-abc-123",
  "actor_id": "user-42",
  "mode": "plan_sql",
  "permissions": { "...": "PermissionsSnapshot JSON" }
}
```

Payload message (JSON string trong AgentRequest):

```json
{
  "brief": { "intent": "...", "filters": { "card_prefix": "E" } },
  "inbox": {},
  "attempt": 1,
  "schema_context": { "tables": ["STRANS", "PMTRANS"] },
  "retrieval_context": ["excerpt từ mongo hybrid..."]
}
```

Headers HTTP: `X-Trace-Id`, `X-Analysis-Id` nếu `set_trace` đã gọi; plus `internal_auth_headers()` cho service-to-service auth.

**Edge:** Circuit mở sau N lỗi — `invoke` raise `AgentUnavailableError` trước khi POST; chat-gateway trả lỗi 5xx hoặc message thân thiện tùy orchestrator.

### §Z.2.12.10 — Ví dụ `HttpSqlGatewayClient.execute_readonly`

Sau III approve, pipeline gọi:

```python
client.execute_readonly(
    "SELECT TOP 50000 STK_ID, SUM(AMOUNT) AS amt FROM STRANS WHERE TRANS_CODE='113' GROUP BY STK_ID",
    acl,
    target_db="db2",
)
```

`_acl_args(acl)` merge `allowed_tables`, `store_ids`, `store_filter_required` vào body POST `/tools/execute_readonly`.

Response điển hình: `rows`, `columns`, `parquet_path` hoặc tương đương — IV đọc qua `dataset_manifest`.

**Edge `SQL_GATEWAY_INPROCESS=1`:** `_call` import `sql_gateway.tools_impl.execute_readonly` — không qua HTTP; phù hợp unit test local.

### §Z.2.12.11 — Ví dụ cache `load_effective_permissions`

User `user-42` login lúc T0 — query DB, cache `(expiry=T0+60s, PermissionSet)`.

Trong 60 giây, mọi `/chat` dùng cache — không query `role_permissions` / `user_permissions`.

Admin revoke quyền `validate_sql` lúc T0+30s — user vẫn có quyền trong cache đến T0+60s.

**Edge:** `AUTH_PERMISSIONS_CACHE_TTL=0` hoặc rất nhỏ — gần như mọi request hit DB; tăng tải AUTH SQL Server.

### §Z.2.12.12 — Ví dụ `GET /artifacts/{trace_id}/{file_name}`

Client đã có JWT hợp lệ:

`GET /artifacts/550e8400-e29b-41d4-a716-446655440000/chart_vip.png?session_id=sess-abc-123`

1. `invalid_path` check — tên file không chứa `..`.
2. Path = `ARTIFACTS_DIR/550e8400.../out/chart_vip.png`.
3. `record_artifact_download` nếu `session_id` query có.
4. `FileResponse` stream PNG.

**Edge:** `file_name=../../etc/passwd` → 400 `invalid_path` trước khi đọc filesystem.

### §Z.2.12.13 — Ma trận phụ thuộc kế thừa `SupermarketAgentService`

| Phương thức kế thừa | Agent I | II | III | IV | Ghi chú |
|---------------------|---------|----|----|-----|---------|
| `parse_payload` | — | ✓ | ✓ | ✓ | I đọc message trực tiếp trong `_ingress` |
| `json_response` | ✓ | ✓ | ✓ | ✓ | Chuẩn hóa AgentResponse |
| `llm_system_prompt` | ✓ | ✓ | ✓ | skill_reference | IV dùng cho test tooling |
| `resolve_permissions` | — | ✓ | ✓ | ✓ | I không check tool trong service |
| `retrieve` | — | ✓ | — | — | Chỉ II có retriever inject |
| `build_context` | — | — | — | — | Có thể dùng qua runner, không trong service.py |

### §Z.2.12.14 — Tham chiếu kiểm thử unit/integration cho 8 tệp

| Tệp | Test module | Ghi chú |
|-----|-------------|---------|
| conversational_router/service.py | `packages/project-test/unit/agents/test_agent_I.py` | Stub ALLOW_LLM_STUB, object.__new__ service |
| sql_planner/service.py | `test_agent_II.py` | Stub plan, clarify VIP |
| risk_reviewer/service.py | `test_agent_III.py` | Policy + stub token |
| data_analyst/service.py | `test_agent_IV.py` | skill_reference, permissions |
| app.py + auth | `integration/test_auth_login.py` | dev-login, monkeypatch authenticate |
| clients.py | `integration/test_orchestrator_wiring.py` | patch HttpAgentInvoker |
| auth_store.py | `integration/test_auth_login.py` | fake authenticate |

Các test trên **không** thay thế đọc mã nguồn — chúng xác nhận hành vi documented tại §Z.2.

### §Z.2.12.15 — Checklist vận hành khi debug 8 tệp

1. **Agent không phản hồi:** Kiểm `AGENT_*_URL`, `/health/ready` agents map, circuit breaker trong `HttpAgentInvoker`.
2. **401 mọi route:** JWT hết hạn, `JWT_SECRET` đổi giữa login và request, hoặc thiếu `ALLOW_DEV_AUTH` ở local.
3. **403 permissions_unavailable:** `AUTH_DB_DSN`, `load_effective_permissions` trả None — không phải lỗi trong 8 tệp service agent mà ở orchestrator.
4. **SQL không chạy:** Chuỗi II `impossible` → quyền `validate_sql`; III `reject` → policy; gateway 404 → `SQL_GATEWAY_URL`.
5. **IV không tạo chart:** `tool_not_granted` trong response; kiểm RBAC `run_analysis_script` và sandbox container.
6. **Stub vs production:** `ALLOW_LLM_STUB=1` bỏ qua OpenRouter ở I/II/III — hành vi khác biệt lớn so prod.

*Hết §Z.2.12 — phụ lục ví dụ và vận hành cho 8 tệp mã nguồn §Z.2.1–§Z.2.8.*

### §Z.2.6.30 — Phân tích dòng-by-dòng `run()` dòng 79–120

**Dòng 79 `trace_id = str(uuid4())`:** Mỗi lần gọi `run()` sinh trace mới độc lập với các lần trước trong cùng session; trace_id là khóa thư mục `data/artifacts/<trace_id>/` và correlation audit Mongo/Redis nếu downstream log theo trace.

**Dòng 80 `analysis_id = workflow.active_analysis_id or trace_id`:** Orchestrator gán `active_analysis_id` khi `start_analysis()` — giữ cùng analysis_id xuyên clarify/resume; nếu workflow chưa có (test đơn lẻ) fallback trace_id để không null.

**Dòng 81 `sync_deadline = deadline`:** Tham số deadline do caller truyền (orchestrator: `monotonic() + max_sync_seconds`) có ưu tiên trước config nội bộ.

**Dòng 82–83:** Chỉ derive deadline từ config khi caller không truyền và `max_sync_seconds` truthy — giá trị 0 hoặc None tắt timeout đồng bộ nội pipeline.

**Dòng 84 `acl = SqlAclContext.from_permissions(permissions)`:** Chuyển snapshot tĩnh thành object gateway hiểu — gồm actor_id, role, phạm vi store để sql-gateway inject predicate WHERE.

**Dòng 85–86 `hasattr set_trace`:** HttpAgentInvoker/HttpSqlGatewayClient có thể gắn header X-Trace-Id; pipeline không import cụ thể client — duck typing.

**Dòng 87–88:** Đặt workflow RUNNING trước vòng lặp; sql_attempt=1 sẽ bị ghi đè ở dòng 130 mỗi vòng — dòng 90 là giá trị khởi tạo trước loop.

**Dòng 91:** Budget guard bọc TraceBudget — mỗi `record("II")` tăng counter theo policy giới hạn agent/phiên.

**Dòng 92–94:** Đường artifact tách raw (SQL parquet) và out (chart CSV/PNG từ IV).

**Dòng 95–96 mkdir:** Tạo thư mục sớm để execute SQL không fail giữa chừng vì thiếu parent dir.

**Dòng 98–104 PolicyEngine:** Catalog + 4 ràng buộc permissions — validate trước khi tốn chi phí agent III và DB.

**Dòng 106 inbox:** Dict mutable một lần `run()` — không serialize Redis; mất khi process crash giữa run.

**Dòng 107 needs_clarification:** Chỉ dùng khi return sớm; không dùng ở `_finish` thường.

**Dòng 108–110 domain_excerpt:** Chuỗi rule domain cho prompt II/IV — rỗng nếu không có store.

**Dòng 112–113 decompose:** Plan bắt buộc trước rank recipe — decompose đồng bộ CPU, không LLM.

**Dòng 115–117 promoted_tools:** Snapshot lúc đầu run — không refresh giữa sql_attempt.

**Dòng 119 `for sql_attempt`:** Vòng ngoài retry toàn pipeline SQL+IV khi data_feedback hoặc không query_files.

**Dòng 120–129 deadline:** Fail-fast ERROR không exception — orchestrator nhận outcome error trong PipelineResult.

**Dòng 130 sql_attempt gán workflow:** UI poll `analysis_status` thấy attempt hiện tại.

**Dòng 131–132 data_feedback:** Merge brief trước II — intent/filter cập nhật cho planner.

### §Z.2.6.31 — Phân tích dòng-by-dòng `run()` dòng 134–210

**Dòng 134 record II:** Một lần mỗi sql_attempt — không record lại trong vòng từng query SQL.

**Dòng 135 schema_bundle:** Chỉ bảng trong allowed_tables — giảm token LLM II.

**Dòng 136–137 shard_plan:** Gợi ý DB shard từ brief + catalog — merge dict vào schema_context.

**Dòng 138–142 filtered_snapshot:** Context policy có thể ẩn cột nhạy cảm khỏi excerpt agent.

**Dòng 143–144 domain_rules_excerpt:** Key riêng với filtered_snapshot — LLM đọc rule nghiệp vụ.

**Dòng 145–147 retrieval:** FeedbackLoop RAG — list object hoặc string; dòng 159 text hóa.

**Dòng 149–150 PLAN_SQL progress:** Callback lưu Redis nếu poll_enabled.

**Dòng 152–163 invoke II:** inbox giữ policy_feedback/risk_feedback từ attempt trước — II đọc để sửa SQL.

**Dòng 164–172 parse II:** ContractInvalidError message vào caveats — debug schema agent.

**Dòng 173–179 isinstance SqlPlannerResponse:** Phòng invoker trả nhầm agent response.

**Dòng 180 action:** Chuỗi điều khiển — không enum cứng trong pipeline (LLM có thể sáng tạo action lạ → continue).

**Dòng 182 exploration_mode guard:** exploration_mode=True bỏ qua return clarify — user đã chọn khám phá không hỏi lại.

**Dòng 183 clarify_round++:** Tích lũy trên workflow object — persist qua STM khi on_progress save.

**Dòng 184–193 CLARIFY step:** step_id uuid mới; summary từ reason clarification.

**Dòng 194–198 vượt max_clarify_rounds:** unknown → exploration; else exception cho orchestrator retry exploration.

**Dòng 199–209 return clarify:** workflow AWAITING_CLARIFICATION; PipelineResult không qua _finish — status clarify khác IDLE.

### §Z.2.6.32 — Phân tích dòng-by-dòng `run()` dòng 211–280

**Dòng 211–220 impossible II:** Kết thúc sớm IMPOSSIBLE — không thử SQL.

**Dòng 222–223 action lạ:** continue sql_attempt — có thể infinite useless retry nếu II luôn trả action sai và max_sql_retries>1.

**Dòng 225–228 trích lists:** sql_queries có thể rỗng — dẫn tới not query_files.

**Dòng 229 default_db db2:** Legacy default database shard siêu thị.

**Dòng 230–232 khởi tạo lists:** profiles/query_files/approved_sql per attempt — reset mỗi sql_attempt.

**Dòng 233–235 max_queries cap probe:** probe_sql tối đa 3 câu dù config cao hơn.

**Dòng 237 for idx sql:** enumerate từng câu trong plan — thứ tự execute tuần tự.

**Dòng 238 tdb:** Index target_dbs — mismatch len → default_db.

**Dòng 239 validate:** PolicyEngine deterministic — không LLM.

**Dòng 240–255 policy reject:** Không break attempt — thử query khác; inbox policy_feedback cho II.

**Dòng 257 sanitized:** Dùng SQL đã strip comment/nguy hiểm nếu engine sanitize.

**Dòng 258–259 approved flags:** approved False đến khi III approve; explain_attached tránh explain lặp.

**Dòng 260 risk loop:** max_risk_retries lần gọi III mỗi query — inbox risk_feedback tích lũy.

**Dòng 261 record III:** Budget per risk attempt — 3 retry = 3 record III.

**Dòng 262–277 invoke III:** explain_plan từ inbox nếu đã có từ lần explain trước.

**Dòng 278–286 parse III:** ContractInvalidError → ERROR toàn pipeline.

**Dòng 287–293 invalid_agent_iii:** Type guard tương tự II.

**Dòng 294–296 approve break:** Thoát risk loop sớm.

**Dòng 297 risk_feedback inbox:** II không đọc trực tiếp — chỉ III lần sau cùng query trong cùng attempt... thực tế cùng query retry III.

**Dòng 298–301 needs explain:** III flag hoặc heuristic keyword trong issue.

**Dòng 302–313 explain path:** Gateway explain + audit; explain_attached=True.

**Dòng 314–323 no explain permission:** POLICY_BLOCKED finish — không execute SQL mù.

### §Z.2.6.33 — Phân tích dòng-by-dòng `run()` dòng 325–422

**Dòng 325–337 not approved:** RISK_REJECT step; continue query tiếp — attempt vẫn có thể có query khác approved.

**Dòng 339–348 validate_sql grant:** Tool capability II — tách với execute_readonly.

**Dòng 350–359 execute_readonly grant:** Quyền chạy SELECT qua gateway.

**Dòng 361–362 EXECUTE progress:** Client thấy đang chạy DB.

**Dòng 363 execute_readonly call:** ACL + target_db — gateway có thể reject thêm policy runtime.

**Dòng 364–386 gateway policy_blocked:** Khác policy engine local — gateway có rule bổ sung; audit outcome policy_blocked.

**Dòng 387 rows:** List dict hoặc empty — DataFrame vẫn tạo được.

**Dòng 388–396 audit ok:** row_count len(rows) — không estimate.

**Dòng 397–399 parquet:** index=False — cột index không ghi file.

**Dòng 400 build_result_profile:** Thống kê dtype, null, sample cho IV.

**Dòng 401–410 QueryResultFile:** path string absolute/relative tùy Path; columns astype str.

**Dòng 411 approved_sql:** List SQL đã chạy thành công — đưa feedback_loop trace_artifacts.

**Dòng 412–422 EXECUTE step:** summary rows và role từ query_meta — UI timeline.

### §Z.2.6.34 — Phân tích dòng-by-dòng `run()` dòng 424–503

**Dòng 424 not query_files:** Mọi query fail policy/risk/gateway — không vào IV.

**Dòng 425–431 hết retry:** POLICY_BLOCKED — không phân biệt policy vs risk trong outcome này.

**Dòng 432 continue:** Thử sql_attempt tiếp với inbox đầy feedback.

**Dòng 434 ExtractedDataset:** Manifest cho IV — trace_id + query files.

**Dòng 435 merge profiles:** Tổng row_count multi-query; columns lấy query đầu.

**Dòng 436–438 IV budget và SANDBOX progress.**

**Dòng 440 analysis_tools = promoted_tools:** Reference không copy — cùng list.

**Dòng 441–442 recipe_candidates accum:** Flat list kèm subtask_id.

**Dòng 444–447 _function_allowed:** Closure đọc permissions và context_policy — recipe inline không tool_id luôn allowed về mặt function (sandbox grant riêng ở IV).

**Dòng 449–458 loop subtasks:** Mỗi subtask rank riêng candidates_by_subtask[id].

**Dòng 460 paths_for_plan:** Chỉ path string parquet — IV đọc file.

**Dòng 461–467 build_execution_plan:** coverage_preview bỏ qua `_` — không dùng trong pipeline.

**Dòng 469–486 invoke IV:** execution_plan list model_dump; iv_max_steps từ config.

**Dòng 487–495 parse IV ContractInvalidError.**

**Dòng 496–502 invalid_agent_iv.**

**Dòng 503 iv_action:** complete, partial, data_feedback, suggest_clarify, impossible, ...

### §Z.2.6.35 — Phân tích dòng-by-dòng `run()` dòng 505–649

**Dòng 505–517 data_feedback validate:** except broad Exception — fallback DataFeedback invalid; inbox ghi lại fb.model_dump().

**Dòng 518–527 DATA_FEEDBACK step:** summary = fb.issue.

**Dòng 528–538 diagnosis impossible:** finish IMPOSSIBLE empty_reason.

**Dòng 539–549 suggest_clarify trong data_feedback:** Return clarify không cần action suggest_clarify riêng.

**Dòng 550–551 needs_probe:** inbox probe_mode — II stub/LLM đọc probe.

**Dòng 552–554 stage_candidate rules:** Domain rule store Mongo staging.

**Dòng 555 continue:** Quan trọng — quay sql_attempt không return.

**Dòng 557–567 action suggest_clarify:** Tách khỏi data_feedback path.

**Dòng 569–579 impossible IV:** explanation_vi ưu tiên cho caveats user-facing synthesize.

**Dòng 581–592 complete/partial sandbox_steps:** Log số bước sandbox đã chạy.

**Dòng 593–594 SYNTHESIZE progress:** Agent I synthesize ở orchestrator sau run return.

**Dòng 595–604 TechnicalSummary:** artifact_urls = out_dir / basename — không URL HTTP đầy đủ.

**Dòng 605–624 registry staging:** Import lazy RecipeStep trong loop new_steps — tránh circular import lúc module load.

**Dòng 615–624 stage_from_run:** Khi có analysis_script mà không new_steps — promote script chạy được.

**Dòng 625–641 on_pipeline_complete:** trace_artifacts dict lớn cho case study indexer — correction_path = sql_attempt>1.

**Dòng 642 return _finish success/partial.**

**Dòng 644–649 exhausted:** Mọi sql_attempt không return thành công — ERROR generic.

### §Z.2.6.36 — Ma trận outcome `run()` và điều kiện kích hoạt

| Outcome | Điều kiện điển hình | workflow.status khi return |
|---------|---------------------|----------------------------|
| NEEDS_CLARIFICATION | II/IV clarify | AWAITING_CLARIFICATION |
| IMPOSSIBLE | II/IV impossible | IDLE qua _finish |
| POLICY_BLOCKED | thiếu quyền explain/execute; hết retry không query | IDLE |
| ERROR | contract invalid, deadline, exhausted | IDLE |
| SUCCESS/PARTIAL | IV complete/partial | IDLE |
| (exception) ClarifyRoundsExceeded | clarify vượt ngưỡng, không unknown | không set — exception |

### §Z.2.6.37 — Sơ đồ luồng văn bản `run()`

```
run(brief, workflow, permissions)
  ├─ init trace, acl, dirs, policy, inbox
  ├─ decompose brief nếu cần
  └─ for sql_attempt in 1..max_retries
       ├─ deadline? → ERROR
       ├─ merge data_feedback → brief
       ├─ invoke II plan_sql
       ├─ clarify? → NEEDS_CLARIFICATION hoặc exploration
       ├─ impossible? → IMPOSSIBLE
       ├─ for each sql in plan
       │    ├─ policy validate
       │    ├─ loop III risk
       │    ├─ explain nếu cần
       │    └─ execute → parquet
       ├─ no files? → continue attempt
       ├─ invoke IV analyze
       ├─ data_feedback? → continue attempt
       ├─ clarify? → NEEDS_CLARIFICATION
       ├─ impossible? → IMPOSSIBLE
       └─ complete/partial → SUCCESS + registry + feedback
  └─ exhausted → ERROR
```

### §Z.2.6.38 — Phụ thuộc inject và test double

Unit test có thể truyền `AgentInvoker` giả trả SqlPlannerResponse cố định và `SqlGatewayClient` trả rows mock — không cần HTTP. `catalog` có thể inject in-memory. `on_progress` list append để assert progress_step sequence.

### §Z.2.6.39 — Không nằm trong pipeline (ranh giới trách nhiệm)

- Gọi agent I ingress/synthesize/clarify: `ChatOrchestrator`.
- Lưu `WorkflowState` Redis: `RedisSessionStore` qua callback.
- `load_effective_permissions` AUTH DB: orchestrator `_build_permissions`.
- JWT auth: chat-gateway `app.py`.
- User message tiếng Việt: agent I.

---

## §AD.0 — Tiếp nối §AC: Domain SQL (`project_core/domain/sql/`)

Năm module: `policy_engine.py`, `shard_resolver.py`, `sql_template_parameterizer.py`, `analysis_script_parameterizer.py`, `result_profile.py`. Chúng phục vụ Agent II/III (validate/plan), pipeline (shard hint), registry promote (parameterize), và profiling sau execute.

---

## §AD.1 — `policy_engine.py`

**Đường dẫn:** `packages/project-core/src/project_core/domain/sql/policy_engine.py`

**Phụ thuộc:** `sqlglot` (dialect tsql), `SchemaCatalog`, `load_project_config().policy`.

### AD.1.1 — `PolicyVerdict` dataclass

| Field | Kiểu | Ý nghĩa |
|-------|------|---------|
| `allowed` | bool | SQL có được phép thực thi không |
| `sanitized_sql` | str \| None | SQL sau inject TOP và store filter |
| `violations` | list[str] | Mã lỗi policy |

### AD.1.2 — `PolicyEngine.__init__`

**Tham số instance:**
- `catalog: SchemaCatalog` — bắt buộc
- `allowed_tables`, `denied_columns`, `store_ids`, `store_filter_required` — từ PermissionsSnapshot

**Từ config policy:**
- `max_rows` — inject LIMIT/TOP
- `max_join_depth` — đếm `exp.Join`
- `default_schema` — lưu nhưng validate chủ yếu qua catalog table names

**Nội bộ:**
- `_dictionary_tables = catalog.sql_table_names()` — set tên bảng hợp lệ
- `allowed_tables = catalog.resolve_allowed_sql_tables(allowed_tables)` — map logical → physical
- `denied_columns` — set lower case

### AD.1.3 — `validate(sql) -> PolicyVerdict`

**Bước 1 — Parse:** `sqlglot.parse(sql, read="tsql")`. Exception → `PolicyVerdict(False, violations=[f"parse_error: {exc}"])`.

**Bước 2 — Single statement:** `len(statements) != 1` → violation `single_statement_required`.

**Bước 3 — Select only:** `not isinstance(statement, exp.Select)` → `select_only`.

**Bước 4 — Forbidden patterns:** `_has_forbidden_patterns` — lowercase scan cho `;`, ` insert `, ` update `, ` delete `, ` drop `, ` exec `, ` xp_`.

**Bước 5 — Tables:** Mọi `exp.Table` name lower:
- Không trong dictionary → `table_not_in_dictionary:{table}`
- Không trong allowed → `table_not_allowed:{table}`

**Bước 6 — Columns:** Mọi `exp.Column`:
- `qualified = table.col` hoặc chỉ col
- Nếu qualified hoặc col trong denied_columns → `column_denied:{qualified}`

**Bước 7 — Join depth:** `len(joins) > max_join_depth` → `join_depth_exceeded`.

**Bước 8 — Sanitize:** Nếu không violations:
- `_inject_top(statement)` — thêm LIMIT max_rows nếu chưa có
- Nếu `store_filter_required and store_ids` → `_inject_store_filter`
- Return `PolicyVerdict(True, sanitized_sql=statement.sql(dialect="tsql"))`

### AD.1.4 — `_inject_top(statement)`

Nếu đã có `limit` trong args → giữ nguyên. Else `statement.set("limit", exp.Limit(expression=exp.Literal.number(self.max_rows)))`.

**Lưu ý T-SQL:** sqlglot dùng LIMIT abstraction; export dialect tsql map sang TOP phù hợp.

### AD.1.5 — `_inject_store_filter(statement)`

Tạo điều kiện `STK_ID IN ('id1', 'id2', ...)` với `exp.In` và `Literal.string` cho mỗi store_id.

Merge vào WHERE: nếu đã có where → `exp.And(existing, condition)`; else `exp.Where(condition)`.

**Giả định:** Cột cửa hàng luôn tên `STK_ID` — phù hợp schema supermarket trong data_dictionary.

### AD.1.6 — `sql_fingerprint(sql)`

`re.sub(r"\s+", " ", sql.strip().lower())[:128]` — chuẩn hóa khoảng trắng, cắt 128 ký tự cho cache/dedup audit.

### AD.1.7 — Callers

| Caller | Cách dùng |
|--------|-----------|
| `sql_gateway.tools_impl._policy` | Mỗi validate/explain/execute |
| Agent II | Qua MCP validate_sql |
| Unit test policy | Inject catalog mock |

### AD.1.8 — Bảng violation codes đầy đủ

| Code | Nguyên nhân | Hướng xử lý agent |
|------|-------------|-------------------|
| parse_error:* | SQL không parse được | III/II sửa cú pháp |
| single_statement_required | Nhiều câu hoặc zero | Tách/bỏ |
| select_only | INSERT/CTE write? | Chỉ SELECT |
| forbidden_pattern | DDL/DML/exec | Loại bỏ |
| table_not_in_dictionary:* | Bảng không có trong dictionary | Đổi bảng |
| table_not_allowed:* | ACL role | Đổi scope hoặc từ chối |
| column_denied:* | Cột nhạy cảm | Bỏ cột |
| join_depth_exceeded | Quá nhiều JOIN | Đơn giản hóa |

---

## §AD.2 — `shard_resolver.py`

**Đường dẫn:** `packages/project-core/src/project_core/domain/sql/shard_resolver.py`

**Mục đích:** Gợi ý routing db1 (archive shard theo tháng) vs db2 (hot) từ filter ngày trong brief.

### AD.2.1 — `ShardPlan` (Pydantic BaseModel)

| Field | Default | Mô tả |
|-------|---------|-------|
| `needs_db1` | False | Cần truy vấn archive |
| `needs_db2` | False | Cần truy vấn hot |
| `shards` | [] | Tên physical table shard |
| `cutoff` | None | Ngày cắt rolling |
| `union_hint` | None | Gợi ý UNION cho agent/planner |

### AD.2.2 — `rolling_cutoff(now=None) -> date`

**Quy tắc:** Ngày đầu tiên của tháng **liền trước** so với `now` (hoặc datetime.now()).

Ví dụ mô tả: now = 2026-07-15 → cutoff = 2026-06-01. now = 2026-01-10 → cutoff = 2025-12-01.

**Công thức mã:**
- month == 1 → date(year-1, 12, 1)
- else → date(year, month-1, 1)

### AD.2.3 — `_load_shards_catalog()`

Đọc `ROOT / "data_dictionary" / "db1" / "shards.yaml"`. Không tồn tại → `{}`. Parse `yaml.safe_load`.

### AD.2.4 — `shards_for_range(logical_table, date_from, date_to, catalog=None)`

1. `physical = tables[logical_table].physical_tables` từ catalog
2. Không physical hoặc không có date_from và date_to → return toàn bộ physical
3. Chuẩn hóa start/end; đổi chỗ nếu start > end
4. `start_ym`, `end_ym` format `%Y%m`
5. Với mỗi tên physical: suffix = phần sau `_` cuối; nếu len 6 và digit và start_ym <= suffix <= end_ym → include
6. Return `out or physical` — fallback full nếu không shard nào khớp range

**Ví dụ tên shard:** `STRANS_202503` → suffix `202503`.

### AD.2.5 — `suggest_query_plan(brief, catalog=None, *, now=None)`

**Input brief dict:** Đọc `filters.date_from`, `filters.from_date`, `filters.date_to`, `filters.to_date`.

**Parse date:** None → None; date object giữ; string → `date.fromisoformat(str(d)[:10])`.

**Logical table cố định:** `"STRANS"` trong mã hiện tại.

**needs_db1:** date_from < cutoff HOẶC date_to < cutoff (có giá trị và so với cutoff).

**needs_db2:** date_from >= cutoff HOẶC date_to >= cutoff HOẶC cả hai date None (mặc định hot).

**union_hint:** Khi cả needs_db1 và needs_db2 — chuỗi mô tả union db1 shards (3 tên đầu + ...) với db2 STRANS.

**Không gọi SQL** — chỉ struct gợi ý cho planner LLM hoặc stub.

---

## §AD.3 — `sql_template_parameterizer.py`

**Đường dẫn:** `packages/project-core/src/project_core/domain/sql/sql_template_parameterizer.py`

**Mục đích:** Thay literal nhạy cảm trong SQL và brief values bằng placeholder khi promote template vào registry — tránh leak giá trị cụ thể của một lần chạy.

### AD.3.1 — `_PLACEHOLDER_PATTERNS`

List tuple `(compiled_regex, replacement)`:

| Pattern | Replacement | Khớp |
|---------|-------------|------|
| `\b\d{4}-\d{2}-\d{2}\b` | `:date` | ISO date |
| `\b\d{5,}\b` | `:number` | Số ≥5 chữ số |
| `'...@....'` email regex | `:email` | Email quoted |
| `'0\d{8,10}'` | `:phone` | SĐT VN quoted |

### AD.3.2 — `parameterize_sql(sql: str) -> str`

Lần lượt `pattern.sub(replacement, out)` cho mỗi pattern — thứ tự có thể ảnh hưởng overlap (date trước number).

### AD.3.3 — `parameterize_brief_values(values: dict) -> dict`

**`_walk` đệ quy:**
- dict → walk từng value
- list → walk từng phần tử
- str → nếu bất kỳ pattern search match → return replacement string thay cho toàn bộ str
- khác → giữ nguyên

Dùng khi lưu brief snapshot vào tool metadata mà không lưu PII cụ thể.

---

## §AD.4 — `analysis_script_parameterizer.py`

**Đường dẫn:** `packages/project-core/src/project_core/domain/sql/analysis_script_parameterizer.py`

### AD.4.1 — `parameterize_analysis_script(script: str) -> str`

Hai substitution regex:
1. `r"/[^\s'\"]+\.parquet"` → `:dataset_path`
2. `r"/[^\s'\"]+/out"` → `:output_dir`

**Mục đích:** Recipe promoted không hardcode path máy cụ thể.

### AD.4.2 — `build_tool_record(...) -> dict`

**Tham số:** name, intent_pattern, script, input_schema, output_schema, trace_id, sql_dependencies, parent_tool_id, steps.

**Logic version:** version=2 nếu có parent_tool_id else 1.

**Return dict tool registry:**
- `tool_id`: uuid4 string
- `status`: `"staged"`
- `kind`: `"recipe"` nếu steps > 1 else `"script"`
- `script_template`: parameterize_analysis_script(script)
- `steps`, `sql_dependencies`, `parent_tool_id`, `source_trace_id`, `promote_score`: 0.0

**Caller:** Feedback loop / registry khi IV complete và stage candidate.

---

## §AD.5 — `result_profile.py`

**Đường dẫn:** `packages/project-core/src/project_core/domain/sql/result_profile.py`

### AD.5.1 — `build_result_profile(df: pd.DataFrame) -> ResultProfile`

**Vòng từng cột:**
- `ColumnStat`: name, null_pct = mean isna, distinct_count = nunique dropna, min/max (None nếu empty series)

**Flags:**
- `empty` nếu len(df)==0
- `high_null_rate` nếu bất kỳ cột null_pct > 0.5

**Return:** `ResultProfile(row_count=len(df), columns=columns, flags=flags)`.

**Dùng sau:** `execute_readonly` → pipeline lưu parquet → profile gửi IV trong `analyze_datasets(profile=...)`.

---

## §AE.0 — `sql_gateway/tools_impl.py`

**Đường dẫn:** `mcp-servers/sql-gateway/src/sql_gateway/tools_impl.py`

**Vai trò:** Implementation thực cho MCP SQL — validate, explain, execute, schema snapshot. Mọi entry kiểm `grant_denial` trên `tool_grants` trong `SqlAclContext`.

### AE.0.1 — Module-level state

| Biến | Mô tả |
|------|-------|
| `_catalog` | `SchemaCatalog.from_dictionary_dir()` load một lần |
| `_rate_lock` | threading.Lock cho rate limit |
| `_rate_buckets` | dict actor_id → list timestamp |
| `_semaphore` | Semaphore(SQL_GATEWAY_MAX_CONCURRENT, default 8) |
| `_DSN_BY_DB` | db1→ANALYTICS_DB_DSN, db2→ANALYTICS_DB_DSN_2 |

### AE.0.2 — `_rate_limit(actor_id, *, limit=30, window=60)`

Trong lock: lọc timestamp trong window 60s, nếu >= limit raise `RuntimeError("rate_limit_exceeded")`, else append now.

**Áp dụng:** explain_sql và execute_readonly — không áp validate_sql.

### AE.0.3 — `_acl_from_kwargs(...) -> SqlAclContext`

Nếu `acl` passed → return ngay. Else build `SqlAclContext` từ actor_id, allowed_tables, denied_columns, store_ids, store_filter_required, tool_grants.

**Mặc định actor_id:** `"system"` khi không truyền.

### AE.0.4 — `_tool_denied(ctx, action)`

`grant_denial(ctx.tool_grants, f"tool:sql-gateway:{action}", f"tool_not_granted:sql-gateway:{action}")`.

**Docstring:** Empty tool_grants = unauthorized deny (fail-closed).

### AE.0.5 — `_policy(acl) -> PolicyEngine`

PolicyEngine với `_catalog` và ACL fields từ ctx.

### AE.0.6 — `_resolve_target_db(target_db)`

None/empty → db1. `"db2"` hoặc `"2"` → db2. Còn lại → db1.

### AE.0.7 — `_connect(target_db)`

pyodbc.connect(os.getenv(DSN_KEY), timeout=30). Thiếu DSN → RuntimeError với tên biến env.

### AE.0.8 — `validate_sql(sql, actor_id="system", *, ...) -> dict`

1. Build ctx
2. `_tool_denied(ctx, "validate")` → return denied dict
3. `verdict = _policy(ctx).validate(sql)`
4. Return `{allowed, violations, sanitized_sql}` — không execute DB

### AE.0.9 — `explain_sql(sql, actor_id, target_db="db1", *, ...) -> dict`

1. Deny check action `explain`
2. `_rate_limit(ctx.actor_id)`
3. Validate — không allowed → `{status: policy_blocked, violations}`
4. `sanitized = verdict.sanitized_sql or sql`
5. Trong `_semaphore` và `_connect`: `SET SHOWPLAN_ALL ON; {sanitized}`
6. Return `{plan_rows, status: ok, target_db}` hoặc error message cắt 500

### AE.0.10 — `execute_readonly(sql, ...) -> dict`

1. Deny execute
2. Rate limit
3. Resolve db, validate
4. Blocked → `{error: policy_blocked, violations}`
5. Execute sanitized trong semaphore+connect
6. `fetchmany(50000)` — cap rows ở driver fetch
7. `maybe_decode_row` từng row dict — TCVN3 → Unicode
8. Return `{columns, rows, row_count, target_db}`

### AE.0.11 — `get_schema_snapshot(...) -> dict`

Deny dùng action `explain` (cùng capability explain).

`role = list(ctx.allowed_tables)` — nếu rỗng bundle tables rỗng.

`_catalog.agent_schema_bundle(role)` + `logical_tables` list.

**Không query SQL Server** — chỉ dictionary YAML trên disk.

### AE.0.12 — Biến môi trường sql-gateway

| Biến | Default | Tác dụng |
|------|---------|----------|
| SQL_GATEWAY_MAX_CONCURRENT | 8 | Semaphore connection |
| ANALYTICS_DB_DSN | — | db1 ODBC |
| ANALYTICS_DB_DSN_2 | — | db2 ODBC |

### AE.0.13 — Luồng execute từ pipeline (mô tả)

```text
Pipeline có PermissionsSnapshot
  → SqlAclContext.to_gateway_args()
  → HttpSqlGatewayClient.execute_readonly(sql, **args)
  → tools_impl.execute_readonly
  → grant_denial → PolicyEngine.validate → pyodbc → rows dict
  → parquet + build_result_profile
```

---

## §AF.0 — `python_sandbox/tools_impl.py`

**Đường dẫn:** `mcp-servers/python-sandbox/src/python_sandbox/tools_impl.py`

### AF.0.1 — Hằng và cấu hình

| Tên | Nguồn | Mặc định |
|-----|-------|----------|
| `_MAX_ROWS` | SANDBOX_MAX_ROWS | 200000 |
| `_MAX_SECONDS` | SANDBOX_MAX_SECONDS | 30 |
| `_RUNNER` | Path cạnh module | runner_child.py |

matplotlib backend `Agg` set tại import — headless chart.

### AF.0.2 — `_artifacts_root() -> Path`

`Path(os.getenv("ARTIFACTS_DIR", "data/artifacts")).resolve()`, mkdir parents.

### AF.0.3 — `_guard_output_dir(output_dir) -> Path`

Resolve output; phải `relative_to(artifacts_root)` else `ValueError("output_dir_must_be_under_artifacts_root")`. mkdir output.

**Bảo mật:** Ngăn script ghi ra ngoài thư mục artifact được phép.

### AF.0.4 — `load_dataset(path) -> dict`

File không tồn tại → `{error: file_not_found, path}`.

Đọc parquet hoặc csv. Cắt head `_MAX_ROWS` nếu vượt.

Return columns list str, row_count, preview 20 records dict orient records.

### AF.0.5 — `preview_dataframe(path, n=100)`

Delegate load_dataset; return `{preview: preview[:n]}`.

### AF.0.6 — `run_analysis_script(path, script, output_dir, tool_grants=None)`

**Defense in depth:** Nếu `tool_grants is not None`, check `grant_denial(..., tool:python-sandbox:run_analysis_script)`.

**Thực thi:**
1. `_guard_output_dir`
2. Verify dataset exists
3. `subprocess.run([sys.executable, _RUNNER, dataset, out], input=script, timeout=_MAX_SECONDS, cwd=out, env với MPLBACKEND=Agg)`
4. returncode != 0: parse stdout JSON error hoặc `{error: script_failed, detail}`
5. returncode == 0: parse JSON stdout hoặc glob artifacts fallback

**In-process IV:** Gọi không truyền tool_grants — tin pipeline đã authorize.

### AF.0.7 — `export_excel(path, output_path)`

load_dataset check → read full df → `to_excel(output_path, index=False)`.

### AF.0.8 — `plot_chart(path, output_path, x, y, title="")`

Read df, plt.figure 10x6, plot x/y, title optional, savefig, close.

### AF.0.9 — `run_recipe_tool(tool_id, path, output_dir, params_json="{}", allowed_functions=None)`

Check `function:{tool_id}` trong allowed_functions nếu supplied.

`get_registry()` → None → recipe_registry_unavailable.

Else `reg.invoke_tool(tool_id, dataset_path, output_dir, params)`.

### AF.0.10 — `merge_datasets(primary, secondary, output_path, on="")`

Read left/right parquet or csv. `join_key = on or _guess_join_key`. Có key → left merge right how=left suffixes `""` và `"_ext"`. Không key → concat axis=1.

Write parquet or csv theo suffix output. Return status ok, path, row_count, join_key.

### AF.0.11 — `_guess_join_key(left_cols, right_cols)`

Upper set intersection ưu tiên thứ tự: SKU, BARCODE, STK_ID, PRODUCT_CODE, ITEM_CODE. Return tên cột gốc từ left_cols.

---

## §AF.1 — `runner_child.py`

**Đường dẫn:** `mcp-servers/python-sandbox/src/python_sandbox/runner_child.py`

**Vai trò:** Process con cách ly — `exec` script pandas với builtins giới hạn.

### AF.1.1 — `main() -> int`

**Argv:** `runner_child.py <dataset_path> <output_dir>` — thiếu → JSON error usage, exit 2.

**Stdin:** Toàn bộ script text. Rỗng → `{error: empty_script}`, exit 2.

**local_vars inject:** `pd`, `plt`, `path` (Path dataset resolved), `out` (Path output dir).

**safe_builtins:** chỉ len, str, int, float, range, min, max.

**exec(script, {"__builtins__": safe_builtins}, local_vars)** — không import os/subprocess trong script unless pandas path.

**Exception:** JSON `{error: script_failed, detail}` exit 1.

**Thành công:** List file trong output_dir, print JSON `{status: ok, artifacts: [...]}`, exit 0.

### AF.1.2 — Mô hình đe dọa và giới hạn

| Rủi ro | Giảm thiểu |
|--------|------------|
| Script độc hại | Subprocess + timeout + cwd=output + builtins hạn chế |
| Ghi file tùy ý | Script chỉ nên dùng `out/`; parent guard artifacts root |
| CPU/memory | SANDBOX_MAX_SECONDS; OS kill subprocess |
| Import arbitrary | exec globals không expose import mặc định |

**Hạn chế còn lại:** pandas/matplotlib vẫn có thể tốn RAM trên file lớn — parent cắt rows ở load_dataset nhưng runner đọc full path argv dataset.

---

## §AG.0 — Chi tiết bổ sung `decomposer.py` (từng dòng logic)

**Tệp:** `packages/project-core/src/project_core/domain/analysis/decomposer.py` — 156 dòng.

### AG.0.1 — Dòng 1–15 import

`uuid4` import nhưng không dùng trong decomposer (dùng ở execution_composer). `re` cho split clause. `OpenRouterClient` chỉ LLM path.

### AG.0.2 — Hàm public export

Chỉ ba hàm public thực sự: `decompose_brief`, `decompose_brief_llm`, `decompose_brief_heuristic`. Không có `__all__` — import star sẽ lấy cả private nếu không prefix `_`.

### AG.0.3 — Ma trận quyết định decompose

| use_llm | ALLOW_LLM_STUB | Kết quả |
|---------|----------------|---------|
| True | 0 | LLM → fallback heuristic |
| True | 1 | Heuristic (use_llm false khi env stub) |
| False | * | Heuristic |
| None | 0 | LLM |
| None | 1 | Heuristic |

### AG.0.4 — Kịch bản ví dụ A: intent đa aspect

Input intent: «So sánh doanh thu VIP và tồn kho cửa hàng A»

Detected aspects có thể gồm: revenue, vip, inventory, compare, store — heuristic tạo một subtask per aspect với cùng filters gốc. `is_decomposed=True`.

IV sau đó chạy từng subtask với candidate recipe riêng; execution_composer map dataset_path qua query_meta subtask_id nếu planner gắn.

### AG.0.5 — Kịch bản ví dụ B: intent một câu dài có dấu phẩy

«Doanh thu tháng 1, tháng 2, tháng 3 năm 2025» — một aspect revenue nhưng nhiều token → `_split_clauses` có thể tách 3 mệnh đề → 3 subtask clause với cùng metrics brief.

### AG.0.6 — Kịch bản ví dụ C: LLM trả JSON

LLM trả `{"subtasks":[{"id":"a","intent":"focus revenue","filters":{"month":1}}], "is_decomposed":true}` — merge filters brief với month=1. Nếu LLM omit metrics → subtask metrics=[] rỗng → param_resolver có thể suy từ intent keyword.

### AG.0.7 — Logging

Chỉ một điểm log: warning khi LLM decompose fail. Không log success hay số subtask — observability phụ thuộc caller.

---

## §AG.1 — Chi tiết bổ sung `param_resolver.py`

**Tệp:** 50 dòng — toàn bộ logic trong hai hàm.

### AG.1.1 — Thứ tự ưu tiên group_by (mở rộng)

1. Explicit dimensions từ subtask (ưu tiên hơn brief khi subtask có dimensions non-empty)
2. Explicit dimensions từ brief
3. Keyword store trong intent
4. Keyword temporal trong intent
5. Không set group_by — script generated fallback `month` ở composer

### AG.1.2 — Tương tác filters đặc biệt

`lookup_mode` từ clarification product không tự đổi SQL — Agent II đọc brief.filters; param_resolver chỉ đưa vào params cho recipe Python.

`loyalty_tier` và `card_prefix` thường đi cặp VIP analysis — recipe template đọc params dict thay vì hardcode.

### AG.1.3 — apply_param_schema_defaults edge cases

| Tình huống | Hành vi |
|------------|---------|
| schema có default None explicit | Không gán (điều kiện `is not None`) |
| enum rỗng | Không gán |
| name đã có trong resolved với value None | Không overwrite — None coi là đã set |
| schema nhiều param | Duyệt tuần tự, thứ tự spec quan trọng nếu enum fallback |

---

## §AG.2 — Chi tiết bổ sung `recipe_matcher.py`

### AG.2.1 — Công thức điểm — ví dụ số

Intent tokens: {doanh, thu, vip} (3). Recipe pattern tokens: {vip, card, revenue} (3). Matched {vip} (1).

precision = 1/3 ≈ 0.333, recall = 1/3 ≈ 0.333, score = 0.6*0.333 + 0.4*0.333 ≈ 0.333.

Intent «doanh thu vip card» matched {vip, card} với pattern trên → recall 2/3, precision 2/3 → score cao hơn.

### AG.2.2 — tool_to_candidate và steps rỗng

Tool có intent_pattern khớp tốt nhưng không script_template và không steps → candidate score cao nhưng `can_reuse` false tại composer — rơi generated script.

### AG.2.3 — matched_aspects vs missing_aspects

matched là intersection sorted — dùng debug UI hoặc LLM selector. missing cắt 8 — tránh payload quá lớn; IV coverage gaps lấy missing_aspects từ best recipe khi partial reuse.

---

## §AG.3 — Chi tiết bổ sung `recipe_retriever.py`

### AG.3.1 — Khi query_embedding None

`embed_scores` rỗng → `embed_score=0` → hybrid = 0.45 * token_score. Thứ hạng giống token-only nhưng scale score thấp hơn — cần lưu ý khi so sánh ngưỡng 0.2/0.35 giữa hybrid và token-only paths.

### AG.3.2 — matched_aspects suffix embed

Chuỗi `embed:0.73` append vào matched_aspects — không phải aspect nghiệp vụ; consumer nên filter prefix `embed:` khi hiển thị user-facing.

---

## §AG.4 — Chi tiết bổ sung `recipe_selector.py`

### AG.4.1 — LLM payload không gửi script

Cố ý giảm token và tránh leak script dài — LLM chỉ chọn tool_id và params JSON. Script lấy từ candidate sau khi chọn.

### AG.4.2 — Fallback candidate khi tool_id lạ

`chosen = next(..., candidates[0])` — ID hallucinate vẫn chạy top1 thay vì fail — có thể chọn sai recipe; rationale vẫn ghi llm_selected.

### AG.4.3 — candidate_to_step multi-step gap

Chỉ steps[0] — recipe nhiều bước (kind recipe trong build_tool_record) mất bước 2+ tại execution hiện tại. Registry promote nên flatten hoặc composer cần mở rộng loop steps.

---

## §AG.5 — Chi tiết bổ sung `execution_composer.py`

### AG.5.1 — Diagnosis partial không có reuse

Điều kiện `elif gaps and generated: diagnosis = partial` — có thể partial khi mọi subtask generated và có gap weak_match.

### AG.5.2 — Generated script CARD_NO filter

Dùng `json.dumps(card_prefix)` trong f-string script — an toàn quote cho Python string trong generated code.

### AG.5.3 — describe() fallback

Khi không group được — `df.describe(include='all').transpose()` — output khác format so với agg CSV — IV vẫn tính là đã chạy step; user có thể thấy artifact khác kỳ vọng.

---

## §AG.6 — Ma trận tích hợp module analysis ↔ pipeline (§Z.2.6)

| Bước pipeline | Module analysis |
|---------------|-----------------|
| decompose (optional) | decomposer via iv _coerce_plan |
| rank recipe | recipe_matcher trong _resolve_execution |
| build execution | execution_composer — pipeline §Z.2.6.19 gọi trực tiếp với function_allowed filter |
| analyze | iv_analyzer.analyze_datasets |
| stage tool | build_tool_record từ analysis_script_parameterizer path feedback |

---

## §AG.7 — Ma trận tích hợp access ↔ MCP

| MCP function | capability | ContextPolicy agent |
|--------------|------------|---------------------|
| validate_sql | tool:sql-gateway:validate | II |
| explain_sql | tool:sql-gateway:explain | III |
| get_schema_snapshot | tool:sql-gateway:explain | III |
| execute_readonly | tool:sql-gateway:execute | pipeline can_execute_sql |
| run_analysis_script | tool:python-sandbox:run_analysis_script | IV |
| preview_dataframe | tool:python-sandbox:preview_dataframe | IV |
| merge_datasets | tool:python-sandbox:merge_datasets | IV |
| plot_chart | tool:python-sandbox:plot_chart | IV |
| export_excel | tool:python-sandbox:export_excel | IV |
| run_recipe_tool | function:{id} | allowed_functions |

---

## §AG.8 — Checklist vận hành khi debug domain layer

1. **Plan rỗng:** Kiểm `decompose_brief` output — intent có aspect không?
2. **Không reuse recipe:** So sánh score với 0.35 và có steps không?
3. **missing_dataset gap:** query_meta subtask_id có khớp paths index không?
4. **policy_blocked SQL:** PolicyEngine violations list — table_not_allowed vs parse_error
5. **sandbox script_failed:** Đọc stderr subprocess hoặc JSON detail runner_child
6. **recipe_registry_unavailable:** `set_registry` đã gọi lúc startup chưa?
7. **rate_limit_exceeded:** Giảm tần suất explain/execute hoặc tăng limit trong code (hiện hardcode 30/60s)
8. **output_dir_must_be_under_artifacts_root:** out_dir IV phải nằm dưới ARTIFACTS_DIR

---

## §AH.0 — Phụ lục mở rộng: đọc từng tệp analysis theo thứ tự alphabet

Phụ lục §AH bổ sung chi tiết hàm-level cho tám tệp `domain/analysis/*.py` — bổ sung cho §AB–§AG, không thay thế.

### §AH.1 — `decomposer.py` — bảng hàm đầy đủ

| Hàm | Dòng (xấp xỉ) | Public | Mô tả ngắn |
|-----|---------------|--------|------------|
| `_analysis_prompt` | 30–32 | Không | Đọc markdown prompt |
| `decompose_brief` | 35–44 | Có | Entry orchestrate LLM/heuristic |
| `decompose_brief_llm` | 47–80 | Có | Gọi OpenRouter JSON subtasks |
| `decompose_brief_heuristic` | 83–113 | Có | Keyword + clause split |
| `_single_subtask` | 116–123 | Không | Subtask st-main |
| `_split_clauses` | 126–128 | Không | Regex tách mệnh đề |
| `_subtask_from_clause` | 131–138 | Không | Subtask per clause |
| `_metrics_for_aspect` | 141–144 | Không | Map aspect → metrics |
| `_dimensions_for_aspect` | 147–155 | Không | Map aspect → dimensions |

### §AH.1.1 — Walkthrough `decompose_brief_heuristic` từng nhánh

**Input giả định:** `brief.intent = "Phân tích doanh thu"`, metrics=[], dimensions=[], filters={}.

Bước 1: intent không rỗng. lower = "phân tích doanh thu".

Bước 2: detected = ["revenue"] vì keyword "doanh thu".

Bước 3: len(detected)=1, len(intent.split())=3 < min_tokens_for_split=12 → return single subtask, is_decomposed=False.

**Kết quả:** Một subtask st-main — pipeline không tách VIP/inventory.

**Input giả định 2:** intent dài 15 từ một aspect, có dấu phẩy.

detected=1 nhưng split clauses → 3 phần → 3 subtask st-clause-0..2, is_decomposed=True.

**Input giả định 3:** "VIP và tồn kho"

detected = vip, inventory (và có thể revenue nếu có từ bán) → multi aspect branch → subtask per aspect.

### §AH.1.2 — `decompose_brief_llm` — schema JSON kỳ vọng

LLM được yêu cầu `response_format json_object`. Cấu trúc hợp lệ tối thiểu:

```json
{
  "subtasks": [
    {
      "id": "optional-string",
      "intent": "string",
      "metrics": ["optional"],
      "dimensions": ["optional"],
      "filters": {"optional": "object"}
    }
  ],
  "is_decomposed": true
}
```

Trường thiếu trong subtask item → fallback brief field tương ứng.

Không validate JSON schema bằng Pydantic second pass — malformed subtask có thể gây lỗi AnalysisSubtask validation.

### §AH.1.3 — Tương tác env ALLOW_LLM_STUB

| ALLOW_LLM_STUB | decompose_brief(use_llm=None) | decompose_brief_llm trực tiếp |
|----------------|------------------------------|------------------------------|
| unset / 0 | LLM path | LLM |
| 1 | heuristic | heuristic ngay đầu hàm |

`recipe_selector` cùng pattern env — đồng bộ stub toàn pipeline local.

---

### §AH.2 — `execution_composer.py` — bảng hàm đầy đủ

| Hàm | Public | Vai trò |
|-----|--------|---------|
| `build_execution_plan` | Có | Main entry |
| `_path_for_subtask` | Không | Map subtask → parquet path |
| `_generated_step_for_subtask` | Không | Script pandas fallback |

### §AH.2.1 — Pseudocode `build_execution_plan`

```text
FOR subtask IN plan.subtasks:
  path ← resolve_path(subtask)
  candidates ← candidates_by_subtask[subtask.id] OR []
  IF brief AND candidates:
    chosen, params, rationale ← select_recipe_for_subtask(...)
  ELSE:
    params ← resolve_params(brief, subtask) if brief else {}
  best ← chosen OR first(candidates) OR None
  reuse_score ← best.score if best else 0
  IF best AND (chosen OR reuse_score >= min_reuse_score) AND best.steps:
    append reuse ExecutionStepPlan
    record reused, gaps from missing_aspects, status partial_reuse|reuse
  ELSE:
    append generated ExecutionStepPlan
    record generated, gap weak_match|no_recipe, status generated
END FOR
compute diagnosis full|partial
RETURN steps_out, ExecutionCoverage
```

### §AH.2.2 — Giá trị `subtask_status` có thể

| Giá trị | Ý nghĩa |
|---------|---------|
| reuse | Recipe reuse hoàn toàn, không missing_aspects |
| partial_reuse | Reuse nhưng candidate báo missing_aspects |
| generated | Không đủ điều kiện reuse |

### §AH.2.3 — Generated script — biến sandbox

Script template literal expect trong child process:

| Biến | Nguồn runner_child |
|------|---------------------|
| pd | pandas module |
| plt | matplotlib pyplot |
| path | Path dataset argv[1] |
| out | Path output argv[2] |

Không inject `json`, `os`, `open` — script chỉ dùng pandas IO qua path/out.

---

### §AH.3 — `iv_analyzer.py` — bảng hàm đầy đủ

| Hàm | Public | Ghi chú |
|-----|--------|---------|
| `_sandbox` | Không | Lazy import tools_impl |
| `analyze_datasets` | Có | Main IV domain entry |
| `_coerce_plan` | Không | Plan từ arg hoặc decompose |
| `_resolve_execution` | Không | execution_plan hoặc compose |
| `_merge_external_paths` | Không | Upload user files |
| `_column_names` | Không | Đọc header parquet/csv |
| `_is_impossible_analysis` | Không | Heuristic impossible |
| `_identifier_mismatch_feedback` | Không | Probe có, main không |
| `_empty_feedback` | Không | row_count profile 0 |
| `_product_clarify` | Không | ClarificationRequest VI |
| `_exploration_clarify` | Không | Hỏi hướng khám phá |

### §AH.3.1 — Action payload IV — bảng đầy đủ

| action | Điều kiện trả về | Pipeline xử lý |
|--------|------------------|----------------|
| complete | coverage không partial, không impossible/clarify | SUCCESS synthesize |
| partial | coverage.diagnosis == partial | PARTIAL synthesize |
| data_feedback | identifier mismatch hoặc empty | sql_attempt retry |
| suggest_clarify | exploration_clarify | NEEDS_CLARIFICATION |
| impossible | metric not mappable | IMPOSSIBLE finish |

### §AH.3.2 — Thứ tự kiểm tra trong `analyze_datasets`

1. identifier_mismatch (main_rows/probe_rows/product_code)
2. empty profile row_count
3. coerce plan, merge datasets
4. resolve execution
5. preview loops
6. exec_steps loops
7. chart optional
8. exploration_clarify early return
9. impossible check
10. complete/partial payload

Thứ tự quan trọng: exploration clarify trước impossible khi exploration_mode và main_rows>0.

### §AH.3.3 — `apply_params_to_script` (registry feedback)

Không nằm trong iv_analyzer file nhưng gọi tại dòng 115 — thay thế placeholder trong script_template bằng params dict. Chi tiết implementation trong `analysis_tool_registry` package feedback; IV phụ thuộc substitution đúng trước subprocess.

---

### §AH.4 — `param_resolver.py` — từng dòng logic

**Dòng 9–14:** Khởi filters merged.

**Dòng 15:** `params = {}` fresh dict mỗi lần gọi — không mutate brief.

**Dòng 17–24:** Four filter keys → params string hóa.

**Dòng 26–32:** group_by inference chain.

**Dòng 34–40:** time_range từ brief (không subtask override time).

**Dòng 42–43:** make_chart boolean.

**Dòng 45–47:** metric first element.

**Dòng 49:** return params — có thể `{}` nếu brief minimal.

**apply_param_schema_defaults dòng 52–64:** Không deep copy nested values trong resolved — shallow copy top level.

---

### §AH.5 — `recipe_matcher.py` — từng hàm

**`_tokenize`:** Set comprehension — không dedupe stem tiếng Việt.

**`score_recipe_against_intent`:** Tuple return 3 phần — caller unpack.

**`tool_to_candidate`:** Round score 4 decimals — tránh float noise sort.

**`rank_candidates`:** List slice sau filter — không dedupe tool_id trùng.

**`_steps_from_tool`:** RecipeStep validate — invalid step dict raise ValidationError.

---

### §AH.6 — `recipe_retriever.py` — toàn tệp

Chỉ một hàm public `hybrid_rank_candidates`. File 45 dòng — wrapper mỏng trên rank_candidates + cosine.

**Khi embed query và tool embedding dimension khác:** `_cosine` behavior phụ thuộc mongo_vector implementation — có thể trả 0 hoặc exception; không catch trong retriever.

**token_weight + embed_weight:** Không normalize về 1.0 nếu chỉ có token — hybrid max về lý thuyết 0.45*1 + 0.55*1 = 1.0 nếu cả hai perfect.

---

### §AH.7 — `recipe_selector.py` — từng hàm

**`select_recipe_for_subtask`:** Entry với try/except broad cho LLM.

**`_select_stub`:** Ngưỡng 0.2 độc lập composer 0.35.

**`_select_llm`:** Profile analyst không router — model có thể khác decomposer.

**`candidate_to_step`:** model_copy step — Pydantic v2 immutable fields.

**Prompt files:** `recipe_select_guide.md` cùng thư mục prompts với decompose_guide.

---

### §AH.8 — `recipe_runtime.py` — toàn tệp

Global mutable `_registry` — không thread lock. Assumption: set_registry once at startup trước concurrent requests.

**Test isolation:** Tests nên gọi set_registry(None) teardown tránh bleed.

---

## §AI.0 — Phụ lục access layer mở rộng

### §AI.1 — `user_claims.py` — case tests mô tả

| raw store_ids | Output |
|---------------|--------|
| None | None |
| [] | None |
| [1, 2, 3] | [1, 2, 3] |
| [1, "", None, 4] | [1, 4] |
| "10, 20 ,30" | [10, 20, 30] |
| "42" | [42] |
| 7 | [7] |

**claims_from_user_dict:** user thiếu `sub` → KeyError — JWT middleware phải validate trước.

### §AI.2 — `permission_set.py` — wildcard ví dụ

| grants | key | granted |
|--------|-----|---------|
| {tool:*} | tool:sql-gateway:execute | True |
| {tool:sql-gateway:*} | tool:sql-gateway:validate | True |
| {tool:sql-gateway:validate} | tool:sql-gateway:execute | False |
| {data:table:STRANS} | data:table:STRANS | True |
| {data:table:*} | data:table:FOO | True via wildcard segment |

**`to_snapshot` denied_columns:** Chỉ keys `data:column_deny:X` không ending `:*`.

### §AI.3 — `acl.py` — so sánh hai path snapshot

| Khía cạnh | permission_set path | yaml role path |
|-----------|---------------------|----------------|
| Nguồn | AUTH DB capabilities | config/project.yaml |
| Wildcard | PermissionSet keys | RoleConfig lists verbatim |
| all_tables expand | Có khi data:table:* | allowed_tables fixed yaml |
| Production | Bắt buộc | ALLOW_DEV_AUTH only |

### §AI.4 — `context_policy.py` — build_request_context ví dụ Agent II

Input: agent="II", session có workflow.brief intent "doanh thu", steps 3, extra inbox data_feedback.

Output ctx keys: agent, actor_id, brief (dict), workflow_steps (list dict), inbox (data_feedback dict).

Agent III ctx chỉ extra — thường schema_context, sql, permissions từ pipeline inject qua extra.

---

## §AJ.0 — Phụ lục SQL domain mở rộng

### §AJ.1 — `policy_engine.py` — sqlglot Select assumptions

Chỉ cho phép root `exp.Select` — CTE `WITH` có thể parse thành structure khác tùy sqlglot version — cần test khi nâng dependency.

**Subqueries:** Table trong subquery vẫn `find_all(exp.Table)` — đếm vào allowed tables.

**Column deny qualified:** Cả `stk_id.column` và `column` alone checked.

### §AJ.2 — `shard_resolver.py` — ví dụ cutoff

| now | cutoff |
|-----|--------|
| 2026-07-03 | 2026-06-01 |
| 2026-01-15 | 2025-12-01 |
| 2026-12-01 | 2026-11-01 |

### §AJ.3 — `shards_for_range` — edge

| date_from | date_to | physical | Kết quả |
|-----------|---------|----------|---------|
| None | None | [A,B,C] | [A,B,C] |
| 202501 | 202503 | STRANS_202502, STRANS_202505 | [202502] hoặc fallback all nếu none match |
| 202512 | 202501 | (swap start>end) | normalized swap |

### §AJ.4 — `sql_template_parameterizer` — thứ tự pattern

Date thay trước number — tránh date bị number pattern ăn phần năm.

Email pattern trước phone — giảm false positive.

### §AJ.5 — `analysis_script_parameterizer.build_tool_record` — field đầy đủ

| Field output | Giá trị |
|--------------|---------|
| tool_id | uuid4 |
| status | staged |
| kind | recipe hoặc script |
| intent_pattern | từ arg |
| input_schema | từ arg |
| output_schema | từ arg |
| script_template | parameterized |
| steps | list hoặc [] |
| sql_dependencies | list hoặc [] |
| parent_tool_id | optional |
| version | 1 hoặc 2 |
| source_trace_id | trace_id |
| promote_score | 0.0 |

### §AJ.6 — `result_profile.py` — ColumnStat edge

Series toàn NaN: null_pct=1.0, distinct_count=0, min/max có thể NaN pandas → Pydantic có thể coerce hoặc fail tùy contract ColumnStat.

Empty dataframe: row_count=0, columns=[], flags=[empty].

---

## §AK.0 — Phụ lục sql_gateway tools_impl mở rộng

### §AK.1 — Thread safety

`_rate_buckets` guarded by `_rate_lock`. `_semaphore` threading.Semaphore — global across requests.

`_catalog` load once — SchemaCatalog assumed immutable sau load.

### §AK.2 — `validate_sql` vs `execute_readonly`

| | validate | execute |
|---|----------|---------|
| rate_limit | Không | Có |
| semaphore | Không | Có |
| pyodbc | Không | Có |
| tool action | validate | execute |

### §AK.3 — `explain_sql` SHOWPLAN

Prefix `SET SHOWPLAN_ALL ON;` + sanitized — một batch string. SQL Server trả plan rows không phải result data.

Exception message cắt 500 ký tự — tránh leak stack ODBC dài.

### §AK.4 — `execute_readonly` fetchmany 50000

Không streaming toàn bộ — memory bound 50k rows * width columns. Policy max_rows inject TOP trước đó giới hạn thêm.

### §AK.5 — `maybe_decode_row`

Từ `project_core.text.tcvn3` — decode tại boundary SQL. Mọi consumer downstream nhận Unicode đúng cho tiếng Việt legacy DB.

### §AK.6 — `get_schema_snapshot` và explain capability

Dùng action explain cho deny check — nghĩa là role cần `tool:sql-gateway:explain` để đọc schema bundle, không cần execute.

### §AK.7 — SqlAclContext integration

Mọi hàm nhận `acl: SqlAclContext | None` — khi Http client gọi, acl đã build từ PermissionsSnapshot.to_gateway_args(). Không truyền acl riêng lẻ khi đã có kwargs grants.

---

## §AL.0 — Phụ lục python_sandbox mở rộng

### §AL.1 — `tools_impl` subprocess model

```text
Parent (tools_impl.run_analysis_script)
  ├─ grant_denial optional
  ├─ _guard_output_dir
  ├─ subprocess.run(runner_child, stdin=script, timeout=MAX_SECONDS)
  └─ parse stdout JSON

Child (runner_child.main)
  ├─ read script stdin
  ├─ exec in restricted globals
  └─ print JSON artifacts list
```

### §AL.2 — Error paths run_analysis_script

| Tình huống | Return |
|------------|--------|
| tool_grants deny | policy_blocked dict |
| output_dir ngoài artifacts | error string guard |
| dataset missing | file_not_found |
| timeout | subprocess TimeoutExpired propagate? — không catch, raise to caller |
| returncode != 0, stdout JSON error | parsed payload |
| returncode != 0, no JSON | script_failed + detail stderr/stdout |
| returncode == 0, invalid JSON | glob artifacts fallback ok |

### §AL.3 — `load_dataset` vs runner read

load_dataset cắt MAX_ROWS cho preview metadata. runner_child đọc full dataset path — file lớn có thể OOM trong child dù parent preview đã cắt.

### §AL.4 — `merge_datasets` concat axis=1

Khi không đoán được join key — wide table concat — có thể duplicate semantic columns; IV log join_key None trong merge result meta.

### §AL.5 — `run_recipe_tool` exception

Broad except → recipe_invoke_failed + detail str(exc) — không re-raise.

### §AL.6 — `runner_child.py` exit codes

| Code | Ý nghĩa |
|------|---------|
| 0 | OK JSON stdout |
| 1 | script exception |
| 2 | usage hoặc empty_script |

### §AL.7 — safe_builtins thiếu

Không có: `print` (script không print debug unless side effect), `open`, `import`, `__import__`, `eval`, `compile`. Script phải dùng pandas read path đã inject.

**matplotlib:** plt.savefig vào out dir — artifact png có thể xuất hiện trong artifacts list.

---

## §AM.0 — Kịch bản end-to-end (mô tả văn bản)

### §AM.1 — Brief đơn giản một subtask reuse recipe

1. Pipeline decompose → một subtask st-main.
2. rank_candidates → tool_id vip_revenue score 0.72.
3. select_recipe_for_subtask LLM chọn tool_id đó.
4. build_execution_plan reuse → ExecutionStepPlan với script template VIP.
5. analyze_datasets chạy run_analysis_script → artifacts csv.
6. action complete, coverage diagnosis full.

### §AM.2 — Brief decomposed partial generated

1. decompose → 3 subtask aspect.
2. Hai subtask có recipe score cao → reuse.
3. Một subtask score 0.1 → generated script groupby.
4. coverage diagnosis partial, action partial, gaps weak_match.

### §AM.3 — Store analyst SQL path

1. build_permissions_snapshot với store_ids [101,102], store_filter_required True.
2. execute_readonly → PolicyEngine inject STK_ID IN ('101','102').
3. Parquet kết quả chỉ cửa hàng được phép.

### §AM.4 — Upload external merge

1. brief.external_sources có parquet_path hợp lệ.
2. _merge_external_paths append role external.
3. analyze_datasets merge_datasets sql + external → merged_upload.parquet prepend paths.
4. IV chạy trên merged.

---

## §AN.0 — Bảng tra cứu nhanh file → hàm public

| File | Hàm public |
|------|------------|
| decomposer.py | decompose_brief, decompose_brief_llm, decompose_brief_heuristic |
| execution_composer.py | build_execution_plan |
| iv_analyzer.py | analyze_datasets |
| param_resolver.py | resolve_params, apply_param_schema_defaults |
| recipe_matcher.py | score_recipe_against_intent, tool_to_candidate, rank_candidates |
| recipe_retriever.py | hybrid_rank_candidates |
| recipe_selector.py | select_recipe_for_subtask, candidate_to_step |
| recipe_runtime.py | set_registry, get_registry |
| user_claims.py | normalize_store_ids, claims_from_user_dict |
| acl.py | role_config, build_permissions_snapshot |
| permission_set.py | capability_granted, tool_capability_for, grant_denial, PermissionSet |
| context_policy.py | ContextPolicy (class methods) |
| policy_engine.py | PolicyEngine, PolicyVerdict |
| shard_resolver.py | rolling_cutoff, shards_for_range, suggest_query_plan, ShardPlan |
| sql_template_parameterizer.py | parameterize_sql, parameterize_brief_values |
| analysis_script_parameterizer.py | parameterize_analysis_script, build_tool_record |
| result_profile.py | build_result_profile |
| sql_gateway/tools_impl.py | validate_sql, explain_sql, execute_readonly, get_schema_snapshot |
| python_sandbox/tools_impl.py | load_dataset, preview_dataframe, run_analysis_script, export_excel, plot_chart, run_recipe_tool, merge_datasets |
| runner_child.py | main |

---

## §AO.0 — Phụ lục cuối: chi tiết mã từng tệp (đủ 2500+ dòng phần domain)

### §AO.1 — `policy_engine.validate` — trình tự kiểm tra từng bước (mã nguồn)

Bước parse sqlglot: dialect `tsql` — phù hợp SQL Server Agent II sinh. Lỗi cú pháp không đi tiếp — trả ngay PolicyVerdict allowed=False.

Kiểm `len(statements) != 1`: multi-statement hoặc empty parse → single_statement_required. Điều này chặn `SELECT 1; SELECT 2` và injection qua dấu chấm phẩy dù forbidden pattern cũng bắt `;`.

Kiểm `isinstance(statement, exp.Select)`: CTE `WITH x AS (...)` có thể được sqlglot parse thành dạng có Select con — behavior phụ thuộc version sqlglot; vận hành cần test regression khi upgrade package.

`_has_forbidden_patterns`: scan lowercase toàn chuỗi SQL gốc, không chỉ AST — bắt substring ` insert ` có space padding tránh false positive `inserted` column tùy context (vẫn có risk false positive tên cột).

Vòng tables: `t.name.lower()` — table không alias vẫn đếm. Alias mapping không resolve tới logical name — tên alias lạ có thể fail table_not_in_dictionary.

Vòng columns: denied check cả qualified và unqualified — role deny `phone` chặn mọi bảng.

Join depth: đếm `exp.Join` nodes — nested join đếm đủ depth config max_join_depth từ project.yaml policy section.

Sau khi pass: `_inject_top` chỉ khi chưa có limit node — SQL đã có TOP/LIMIT user không bị ghi đè.

`_inject_store_filter`: store_ids rỗng nhưng store_filter_required True — vẫn inject IN () rỗng? Mã tạo expressions từ list store_ids or [] — IN rỗng có thể invalid SQL Server; edge case role misconfiguration.

Return sanitized `.sql(dialect="tsql")` string — caller execute trực tiếp chuỗi này.

### §AO.2 — `sql_gateway.execute_readonly` — từng dòng hành vi

Dòng build ctx từ kwargs hoặc acl object — ưu tiên acl khi cả hai (acl wins trong _acl_from_kwargs).

_tool_denied execute action — trả dict policy_blocked shape từ grant_denial, không raise.

_rate_limit có thể raise RuntimeError rate_limit_exceeded — caller HTTP layer phải map 429 hoặc 500; không catch trong tools_impl.

_validate trước connect — không mở connection nếu policy fail tiết kiệm pool.

`with _semaphore, _connect(db)`: acquire semaphore trước connect — giới hạn đồng thời global 8 default.

cur.execute(sanitized) — một statement.

columns từ description metadata.

fetchmany(50000) — không fetchall — bound memory.

maybe_decode_row per row — CPU overhead tuyến tính số hàng; chấp nhận cho 50k cap.

Return dict columns rows row_count target_db — không include sanitized_sql trong response success.

### §AO.3 — `iv_analyzer.analyze_datasets` — biến trung gian đầy đủ

Sau merge paths có thể dài hơn manifest queries gốc — index row_counts vẫn theo manifest queries ban đầu, không extend cho external paths — meta external row_count từ ExternalSource optional.

probe_idxs và main_idxs dựa meta role — probe SQL từ II đánh dấu role probe trong query_meta.

Khi merge thành công paths = [merged] + paths cũ — IV có thể chạy step trên merged trước; preview paths[:2] có thể là merged và sql gốc.

steps_run tăng cả preview và exec và chart — shared budget max_steps.

coverage object mutable — gaps append trong loop budget_exceeded và step_failed — ExecutionCoverage Pydantic model có thể mutate list field gaps in-place tùy version.

new_steps chỉ generated status — reuse không đưa vào promote candidate list.

payload analysis_script chỉ first new_step — các generated khác không expose trong payload top level.

### §AO.4 — `execution_composer._generated_step_for_subtask` — template đầy đủ (mô tả)

Template gồm: import implicit pandas qua pd; đọc file; filter card optional; định nghĩa group_cols list literal; cols intersection; metric string; branch groupby sum hoặc describe; to_csv với tên subtask id.

uuid step_id mỗi lần generate khác — trace log theo step_id.

params json trong RecipeStep — apply_params_to_script có thể thay `{{metric}}` style tùy registry implementation.

### §AO.5 — `recipe_selector._select_llm` — payload và response

User message JSON kích thước ~ brief dump + subtask dump + 5 candidates metadata — không gửi script_template tiết kiệm token.

Response JSON expected keys: tool_id, params dict optional, rationale string, use_none boolean optional.

Khi use_none: return None candidate — composer vẫn có thể reuse nếu score top >= 0.35 và steps exist dù LLM từ chối — vì best = chosen or candidates[0]; nếu chosen None và best score 0.5 → can_reuse true without LLM agreement.

### §AO.6 — `decomposer` — failure modes

OpenRouter timeout: exception → heuristic fallback — user không thấy lỗi API, chỉ plan heuristic.

JSON LLM invalid: exception propagate từ json.loads — không fallback nếu exception xảy ra sau try trong decompose_brief_llm ngoài outer try của decompose_brief — actually decompose_brief_llm json.loads not in try, only decompose_brief wraps decompose_brief_llm in try. So JSON error in LLM path → caught by decompose_brief → heuristic. Good.

AnalysisSubtask validation error trong list comp: also caught by outer try → heuristic.

### §AO.7 — `permission_set.capability_granted` — proof các case

Grant `function:*` covers `function:uuid-tool-id` — wildcard segment function.

Grant `data:*` trong _wants_all_tables — expand all_tables snapshot.

Empty grants frozenset — mọi capability false — dev yaml phải list explicit tool_grants.

### §AO.8 — `context_policy.can_invoke_tool` — double gate

Gate 1: tool name in AGENT_TOOLS agent tuple — agent IV không gọi validate_sql dù có grant.

Gate 2: capability_granted on permissions.tool_grants — có thể fail nếu yaml chỉ cho SQL execute mà không list preview tools.

### §AO.9 — `shard_resolver.suggest_query_plan` — khi date None

needs_db2 True khi date_from và date_to đều None — mặc định hot db2.

needs_db1 False nếu không có date < cutoff — archive không dùng khi không filter thời gian.

union_hint chỉ khi span cả hai DB — planner LLM đọc hint text.

### §AO.10 — `result_profile.build_result_profile` — numeric columns

min max trên series numeric pandas — cột string có min max lexicographic hoặc mixed type warning pandas future.

high_null_rate flag any column > 50% null — một cột junk có thể flag cả dataset.

### §AO.11 — `python_sandbox.merge_datasets` — suffix columns

merge how=left suffixes "" và "_ext" — trùng tên cột right đổi tên _ext.

concat axis=1 without join — row count max left right không align index — pandas align NaN.

### §AO.12 — `runner_child` — security notes mở rộng

exec với globals __builtins__ restricted — user script không gọi open() trừ khi pandas internal gọi.

pandas read_parquet path từ argv — path đã resolve parent — không cho phép path traversal nếu parent validate dataset path exists.

cwd=out dir — script đổi working directory process con — relative write vào cwd trỏ output dir.

timeout kill subprocess — không guarantee kill tree nếu child spawn thêm — subprocess.run không dùng start_new_session.

### §AO.13 — `analysis_script_parameterizer.parameterize_analysis_script`

Regex path unix style `/...parquet` — Windows backslash path có thể không match — artifact paths trong deployment Linux-centric.

output_dir pattern `/.../out` — tương tự.

### §AO.14 — `sql_template_parameterizer.parameterize_brief_values` walk

Nested dict brief filters — leaf string date thay bằng `:date` toàn bộ value — không giữ partial structure.

List values walk từng phần tử — mixed types preserved.

### §AO.15 — Tích hợp Mongo registry (ngoài file nhưng caller)

`rank_candidates` thay bằng registry list tools dict khi pipeline có analysis_tool_registry.

`recipe_candidates` với subtask_id từ pipeline §Z.2.6.19 — skip rank per intent, dùng precomputed list.

`hybrid_rank_candidates` khi retriever embed query — không trong iv_analyzer default path.

### §AO.16 — Glossary tiếng Việt thuật ngữ domain

| Thuật ngữ | Nghĩa trong mã |
|-----------|----------------|
| Brief | AnalysisBrief intent phân tích |
| Subtask | Đơn vị nhỏ sau decompose |
| Recipe / tool | Analysis tool dict script_template |
| Reuse | Chạy script từ registry promoted |
| Generated | Script pandas sinh tự động composer |
| Coverage | ExecutionCoverage diagnosis gaps |
| Capability | Chuỗi quyền permission_set |
| Sanitized SQL | SQL sau TOP và store filter |
| Artifact | File output sandbox dưới ARTIFACTS_DIR |
| Probe | Query role probe kiểm định identifier |

### §AO.17 — Danh sách file đã tài liệu hóa (checklist yêu cầu user)

- [x] packages/project-core/src/project_core/domain/analysis/decomposer.py
- [x] packages/project-core/src/project_core/domain/analysis/execution_composer.py
- [x] packages/project-core/src/project_core/domain/analysis/iv_analyzer.py
- [x] packages/project-core/src/project_core/domain/analysis/param_resolver.py
- [x] packages/project-core/src/project_core/domain/analysis/recipe_matcher.py
- [x] packages/project-core/src/project_core/domain/analysis/recipe_retriever.py
- [x] packages/project-core/src/project_core/domain/analysis/recipe_runtime.py
- [x] packages/project-core/src/project_core/domain/analysis/recipe_selector.py
- [x] packages/project-core/src/project_core/domain/access/user_claims.py
- [x] packages/project-core/src/project_core/domain/access/acl.py
- [x] packages/project-core/src/project_core/domain/access/permission_set.py
- [x] packages/project-core/src/project_core/domain/access/context_policy.py
- [x] packages/project-core/src/project_core/domain/sql/policy_engine.py
- [x] packages/project-core/src/project_core/domain/sql/shard_resolver.py
- [x] packages/project-core/src/project_core/domain/sql/sql_template_parameterizer.py
- [x] packages/project-core/src/project_core/domain/sql/analysis_script_parameterizer.py
- [x] packages/project-core/src/project_core/domain/sql/result_profile.py
- [x] mcp-servers/sql-gateway/src/sql_gateway/tools_impl.py
- [x] mcp-servers/python-sandbox/src/python_sandbox/tools_impl.py
- [x] mcp-servers/python-sandbox/src/python_sandbox/runner_child.py

### §AO.18 — Đếm phạm vi phần bổ sung

Phần `# Phần AB` bắt đầu tại dòng 2913 trong tài liệu này; các mục §AB–§AO mô tả trực tiếp từ mã nguồn các đường dẫn liệt kê §AO.17, không sao chép từ README hoặc CONFIGURATION_CHECKLIST.

### §AO.19 — Bổ sung chi tiết hàm `validate_sql` (sql_gateway)

Hàm `validate_sql` trong `tools_impl.py` là cổng kiểm khô Agent II trước khi SQL vào pipeline execute. Không có side effect database.

Tham số `actor_id` mặc định `"system"` khi gọi nội bộ test — production HttpSqlGatewayClient luôn truyền sub JWT.

Khi `acl` object được truyền, các kwargs `allowed_tables`, `tool_grants` bị bỏ qua — tránh mâu thuẫn ACL duplicate.

Kết quả `allowed: false` vẫn trả `sanitized_sql: null` — client không được execute SQL đã sanitize khi not allowed (khác một số API trả sanitized để debug; ở đây chỉ có khi allowed true sau validate pass).

Violations list có thể nhiều phần tử — Agent II stub không parse; LLM path cần đọc để sửa SQL.

### §AO.20 — Bổ sung `explain_sql` và `get_schema_snapshot`

`explain_sql` dùng cùng policy validate như execute — SQL không hợp lệ không tốn SHOWPLAN roundtrip ngoài parse.

Rate limit áp dụng explain — burst explain từ Agent III có thể hit rate_limit_exceeded RuntimeError.

`get_schema_snapshot` không nhận `target_db` — schema từ file dictionary, không phụ thuộc db1/db2.

Bundle trả về gồm tables excerpt và domain_definitions_excerpt — kích thước phụ thuộc số bảng allowed_tables role.

### §AO.21 — Bổ sung từng tool python_sandbox

`load_dataset`: suffix `.parquet` quyết định reader; extension `.csv` case sensitive trên Linux deployment.

`preview_dataframe`: n default 100 nhưng IV gọi n=30 — không ảnh hưởng load_dataset preview 20 internal cap.

`export_excel`: cần dependency openpyxl/xlsxwriter tùy pandas env — không declare trong tools_impl; thiếu lib raise lúc runtime.

`plot_chart`: plt.plot linear — không phân biệt bar/line theo brief; chart đơn giản exploratory.

`run_recipe_tool`: params_json parse JSON — invalid JSON raise propagate từ json.loads không catch.

### §AO.22 — `iv_analyzer` feedback probe SQL nhúng product_code

`_empty_feedback` sinh suggested_sql với f-string `LIKE '%{product_code}%'` — không escape SQL quote trong product_code — nếu code chứa `'` có thể break SQL hoặc injection khi probe execute. Upstream brief validation nên sanitize.

Tương tự `_product_clarify` hiển thị product_code trong prompt UI — không phải SQL nhưng XSS UI nếu client render raw HTML không escape (ngoài phạm vi backend).

### §AO.23 — `recipe_matcher` token overlap và tiếng Việt

Regex token hỗ trợ Unicode tiếng Việt có dấu — intent không dấu và pattern có dấu có thể không match (ví dụ "doanh thu" vs pattern "doanh thu" OK nhưng user gõ không dấu).

Độ dài token > 2 loại "Q1", "ST" — có thể giảm recall seasonal queries.

### §AO.24 — `param_resolver` metric mặc định generated script

Khi brief không có metrics, generated script dùng AMOUNT — phù hợp STRANS supermarket; brief metric revenue không map cột có thể vẫn chạy AMOUNT nếu params metric không set.

### §AO.25 — `execution_composer` min_reuse_score tuning

Giảm 0.35 → nhiều reuse hơn, rủi ro script recipe không khớp intent. Tăng → nhiều generated describe() fallback.

Tham số không expose env — hardcode default argument; đổi cần sửa mã hoặc caller truyền override.

### §AO.26 — `shard_resolver` logical table cố định STRANS

`suggest_query_plan` không đọc brief table intent — mọi plan shard giả định STRANS. Brief inventory query vẫn nhận shard STRANS hint — có thể misleading planner; cải tiến tương lai đọc schema_context.

### §AO.27 — `build_tool_record` version 2 parent

Khi promote iteration tool, parent_tool_id set → version 2 — registry UI có thể hiển thị lineage; không tự động deprecate parent.

### §AO.28 — `PermissionSet.full_access` dùng khi nào

Test và admin bootstrap — không nên gán production user thật mà không audit; thay bằng keys cụ thể từ AUTH DB.

### §AO.29 — `ContextPolicy` agent V

Không có agent V trong build_request_context — chỉ I–IV. Agent mới cần extend elif branch.

### §AO.30 — `runner_child` artifacts list

`output_dir.iterdir()` mọi file — kể cả file ẩn hoặc temp matplotlib — parent trả về list paths cho IV artifact_paths.

### §AO.31 — Ma trận env vars cross-module (tổng hợp)

| Biến | Module ảnh hưởng |
|------|------------------|
| ALLOW_LLM_STUB | decomposer, recipe_selector |
| ANALYTICS_DB_DSN / _2 | sql_gateway connect |
| SQL_GATEWAY_MAX_CONCURRENT | sql_gateway semaphore |
| SANDBOX_MAX_ROWS / SECONDS | python_sandbox |
| ARTIFACTS_DIR | python_sandbox guard |
| ALLOW_DEV_AUTH | acl yaml fallback (orchestrator) |

### §AO.32 — Kết luận phạm vi tài liệu domain

Toàn bộ mục từ `# Phần AB` (dòng 14259) đến hết §AO.40 document trực tiếp 20 tệp Python liệt kê §AO.17.

### §AO.33 — `decomposer.py` dòng 35–44 (`decompose_brief`)

Dòng 37–38: `use_llm is None` đọc env — pattern nhất quán với `recipe_selector` dòng 31–32.

Dòng 39–43: try/except bọc toàn bộ `decompose_brief_llm` — bất kỳ lỗi nào cũng fallback heuristic, kể cả lỗi mạng OpenRouter và JSON malformed từ LLM (nếu raise trước khi return).

Dòng 44: return heuristic khi `use_llm` false — không gọi LLM dù có API key.

### §AO.34 — `iv_analyzer.py` dòng 95–102 (preview loop)

Vòng `for path in paths[:2]` — chỉ hai dataset đầu được preview, không phải tất cả query trong manifest multi-query.

`preview_dataframe` gọi không truyền `tool_grants` — in-process path tin cậy; MCP HTTP phải truyền grants ở layer gateway.

Metric key `preview_rows_{steps_run}` — steps_run tăng trước khi gán metric nên index 1-based sau lần tăng đầu.

### §AO.35 — `policy_engine.py` dòng 41–86 (`validate` body)

Dòng 48–50: single statement guard trước select-only — thứ tự violation ưu tiên parse → count → type.

Dòng 57–59: forbidden pattern scan raw SQL string song song AST check — defense depth cho injection chuỗi.

Dòng 79–80: early return violations trước sanitize — không leak sanitized SQL khi deny.

Dòng 82–86: chỉ inject TOP và store filter khi allowed — sanitized_sql luôn từ AST đã mutate.

### §AO.36 — `tools_impl.execute_readonly` dòng 200–216

Dòng 200: `_rate_limit` sau deny check — actor bị deny không tốn rate bucket.

Dòng 206–207: `with _semaphore, _connect` — context manager nested; release semaphore khi connection đóng.

Dòng 212–215: list comprehension `maybe_decode_row` — O(n) trên row; bottleneck trên result lớn gần 50k.

Dòng 216: return không gồm `sanitized_sql` — client không thấy SQL đã inject TOP/store.

### §AO.37 — `runner_child.py` dòng 16–41 (`main`)

Dòng 17–19: argv length check — thiếu output_dir → usage error JSON stdout exit 2.

Dòng 23–26: stdin read toàn bộ script — script lớn bị giới hạn bởi OS pipe buffer; thực tế recipe ngắn.

Dòng 27–32: `local_vars` dict mutable — script có thể gán biến mới trong locals qua exec.

Dòng 33: `safe_builtins` thiếu `print` — debug script khó; cố ý giảm side channel.

Dòng 35: `exec(..., {"__builtins__": safe_builtins}, local_vars)` — noqa S102 suppressed bandit.

Dòng 39–40: artifacts mọi file trong output_dir — không lọc extension.

### §AO.38 — `permission_set.AGENT_TOOLS` và Agent IV

Agent IV tuple không gồm `run_recipe_tool` — function capability tách namespace `allowed_functions`. Pipeline `_function_allowed` trong §Z.2.6.19 lọc recipe candidate theo `can_invoke_function`.

Agent IV có `merge_datasets` — IV analyzer gọi trực tiếp khi external upload; không qua AGENT_TOOLS HTTP map nếu in-process import.

### §AO.39 — `context_policy.build_request_context` Agent IV

Nhánh IV chỉ `ctx.update(extra or {})` — pipeline phải đính kèm đủ brief, manifest, permissions trong extra khi invoke; không tự động pull từ session như Agent I/II.

### §AO.40 — Tổng kết số dòng phần domain

Phần bổ sung `# Phần AB` → `*Hết Phần AB–AN*` gồm §AB–§AO.40, mô tả 20 tệp nguồn theo yêu cầu, tiếng Việt, không trích docs markdown khác trong repo.

### §AO.41 — Chỉ mục nhanh theo thư mục mã nguồn

**`domain/analysis/` (8 tệp):** `decomposer.py` tách brief; `param_resolver.py` suy params; `recipe_matcher.py` / `recipe_retriever.py` xếp hạng recipe; `recipe_selector.py` chọn recipe (LLM/stub); `execution_composer.py` lập `ExecutionStepPlan`; `recipe_runtime.py` registry singleton; `iv_analyzer.py` chạy sandbox và trả action IV.

**`domain/access/` (4 tệp):** `user_claims.py` chuẩn hóa JWT; `permission_set.py` capability và `AGENT_TOOLS`; `acl.py` `build_permissions_snapshot`; `context_policy.py` ngữ cảnh agent và `can_invoke_tool`.

**`domain/sql/` (5 tệp):** `policy_engine.py` validate SQL; `shard_resolver.py` gợi ý db1/db2; `sql_template_parameterizer.py` / `analysis_script_parameterizer.py` promote template; `result_profile.py` profile DataFrame.

**MCP:** `sql_gateway/tools_impl.py` validate/explain/execute/schema; `python_sandbox/tools_impl.py` + `runner_child.py` sandbox pandas cách ly.

### §AO.42 — Đường dẫn tuyệt đối trong monorepo (tham chiếu)

| Thành phần | Đường dẫn tương đối repo |
|------------|--------------------------|
| Analysis domain | `packages/project-core/src/project_core/domain/analysis/` |
| Access domain | `packages/project-core/src/project_core/domain/access/` |
| SQL domain | `packages/project-core/src/project_core/domain/sql/` |
| SQL MCP impl | `mcp-servers/sql-gateway/src/sql_gateway/tools_impl.py` |
| Sandbox MCP impl | `mcp-servers/python-sandbox/src/python_sandbox/tools_impl.py` |
| Sandbox runner | `mcp-servers/python-sandbox/src/python_sandbox/runner_child.py` |

Phần domain §AB–§AO.42: mô tả trực tiếp từ mã nguồn các tệp trên (không bao gồm §Z.3 pipeline).

Ghi chú đếm: Phần AB bắt đầu dòng 14259; kết thúc tại dòng Hết Phần AB–AN ngay dưới §AO.42.

---

*Hết Phần AB–AN — tài liệu domain analysis, access, sql, MCP sandbox từ mã nguồn (phụ lục §AH–§AO bổ sung chi tiết).*
