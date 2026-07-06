## §I.1-DETAIL — Mọi khóa trong config/project.yaml

> **Phạm vi:** Giải thích chi tiết từng khóa top-level và nested trong `config/project.yaml`. Stub §I.1 giữ tổng quan; section này là reference đầy đủ.

### §I.1-DETAIL.1 — Khóa scalar và nested

#### `app_name`

- **Nhóm:** `root`
- **Giá trị mặc định (repo):** `supermarket-analysis-agent`
- **Ý nghĩa:** Tên logical app; logging, metrics label.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `pipeline.max_sql_queries_per_plan`

- **Nhóm:** `pipeline`
- **Giá trị mặc định (repo):** `6`
- **Ý nghĩa:** Giới hạn số query SQL trong một plan Agent II; tránh runaway.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `pipeline.max_sql_retries`

- **Nhóm:** `pipeline`
- **Giá trị mặc định (repo):** `3`
- **Ý nghĩa:** Vòng lặp ngoài khi plan/execute fail; mỗi vòng có thể nhận policy/risk feedback.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `pipeline.max_risk_retries`

- **Nhóm:** `pipeline`
- **Giá trị mặc định (repo):** `2`
- **Ý nghĩa:** Số lần Agent III reject trước khi pipeline abort hoặc clarify.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `pipeline.max_clarify_rounds`

- **Nhóm:** `pipeline`
- **Giá trị mặc định (repo):** `3`
- **Ý nghĩa:** Tối đa vòng hỏi user qua clarification bridge.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `pipeline.max_sync_seconds`

- **Nhóm:** `pipeline`
- **Giá trị mặc định (repo):** `120`
- **Ý nghĩa:** Deadline đồng bộ pipeline; timeout → partial/error outcome.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `pipeline.iv_max_steps`

- **Nhóm:** `pipeline`
- **Giá trị mặc định (repo):** `8`
- **Ý nghĩa:** Max bước reasoning Agent IV (analyst).
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `pipeline.poll_enabled`

- **Nhóm:** `pipeline`
- **Giá trị mặc định (repo):** `true`
- **Ý nghĩa:** Cho phép UI poll workflow progress qua STM.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `pipeline.workflow_stale_ttl_seconds`

- **Nhóm:** `pipeline`
- **Giá trị mặc định (repo):** `900`
- **Ý nghĩa:** Workflow cũ hơn 15 phút coi là stale; cleanup/recreate.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `pipeline.workflow_steps_max`

- **Nhóm:** `pipeline`
- **Giá trị mặc định (repo):** `200`
- **Ý nghĩa:** Cap số WorkflowStep ghi vào trace — tránh bloat.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `pipeline.workflow_steps_scope`

- **Nhóm:** `pipeline`
- **Giá trị mặc định (repo):** `analysis`
- **Ý nghĩa:** Scope filter khi persist steps (analysis vs chat-only).
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `clarification.hard_enforce`

- **Nhóm:** `clarification`
- **Giá trị mặc định (repo):** `true`
- **Ý nghĩa:** Bắt buộc clarify khi confidence thấp; không bypass silently.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `clarification.bridge_min_confidence`

- **Nhóm:** `clarification`
- **Giá trị mặc định (repo):** `0.75`
- **Ý nghĩa:** Ngưỡng Agent I bridge chấp nhận brief không cần clarify.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `rag.clarify_min_score`

- **Nhóm:** `rag`
- **Giá trị mặc định (repo):** `0.72`
- **Ý nghĩa:** RAG retrieval score tối thiểu để auto-answer clarify.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `rag.top_k`

- **Nhóm:** `rag`
- **Giá trị mặc định (repo):** `5`
- **Ý nghĩa:** Số chunk retrieval inject vào context.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `budget.agent_caps.I`

- **Nhóm:** `budget`
- **Giá trị mặc định (repo):** `5`
- **Ý nghĩa:** Token/step budget cap Agent I (router).
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `budget.agent_caps.II`

- **Nhóm:** `budget`
- **Giá trị mặc định (repo):** `6`
- **Ý nghĩa:** Cap Agent II (SQL planner).
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `budget.agent_caps.III`

- **Nhóm:** `budget`
- **Giá trị mặc định (repo):** `18`
- **Ý nghĩa:** Cap Agent III (risk — nhiều bước hơn).
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `budget.agent_caps.IV`

- **Nhóm:** `budget`
- **Giá trị mặc định (repo):** `4`
- **Ý nghĩa:** Cap Agent IV (analyst).
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `budget.max_tokens_per_trace`

- **Nhóm:** `budget`
- **Giá trị mặc định (repo):** `200000`
- **Ý nghĩa:** Hard ceiling toàn trace pipeline.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `policy.max_rows`

- **Nhóm:** `policy`
- **Giá trị mặc định (repo):** `50000`
- **Ý nghĩa:** PolicyEngine reject SELECT trả quá N rows.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `policy.max_join_depth`

- **Nhóm:** `policy`
- **Giá trị mặc định (repo):** `5`
- **Ý nghĩa:** Giới hạn độ sâu JOIN — anti-complexity.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `policy.default_schema`

- **Nhóm:** `policy`
- **Giá trị mặc định (repo):** `dbo`
- **Ý nghĩa:** Schema SQL mặc định khi không qualify.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `artifacts.base_dir`

- **Nhóm:** `artifacts`
- **Giá trị mặc định (repo):** `data/artifacts`
- **Ý nghĩa:** Thư mục parquet, explain plans, temp files.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `artifacts.ttl_days`

- **Nhóm:** `artifacts`
- **Giá trị mặc định (repo):** `7`
- **Ý nghĩa:** Retention cleanup (`scripts/cleanup_artifacts.py`).
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `artifacts.max_bytes_per_trace`

- **Nhóm:** `artifacts`
- **Giá trị mặc định (repo):** `52428800`
- **Ý nghĩa:** 50 MiB cap artifact size per trace.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `stm.session_ttl_days`

- **Nhóm:** `stm`
- **Giá trị mặc định (repo):** `30`
- **Ý nghĩa:** Redis/Mongo session expiry cho workflow state.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `data_sources.db1.env_dsn`

- **Nhóm:** `data_sources`
- **Giá trị mặc định (repo):** `ANALYTICS_DB_DSN`
- **Ý nghĩa:** DSN SQL Server shard HQ (db1).
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

#### `data_sources.db2.env_dsn`

- **Nhóm:** `data_sources`
- **Giá trị mặc định (repo):** `ANALYTICS_DB_DSN_2`
- **Ý nghĩa:** DSN DB phụ (db2) nếu có.
- **Loader:** `project_core.config.loader.load_project_config()` merge vào `ProjectConfig`.
- **Override:** env không override trực tiếp — sửa YAML hoặc mount config map K8s.

### §I.1-DETAIL.2 — YAML anchors `_HQ_TABLES` / `_STORE_TABLES`

File dùng YAML anchor/alias để DRY danh sách bảng:
- `&hq_tables` — ~40 bảng HQ (STRANS, PMTRANS, TRANSHDR, CRDTRANS, CUSTOMER, SKU_DEF, WebRpt_*, …).
- `&store_tables` — subset ~15 bảng store-level (bỏ ARC/TMP/admin tables).
- `roles.*.allowed_tables: *hq_tables` hoặc `*store_tables` — alias reference.
**Lưu ý shard:** Comment line 50: SQL runtime có thể dùng `STRANS_YYYYMM`, `PMTRANS_YYYYMM` — logical name trong dictionary khác physical shard table.
**Đồng bộ AUTH DB:** Comment line 111–112: dev/test grants phải mirror `deploy/sql/auth/004_permissions.sql` khi `ALLOW_DEV_AUTH=1`.
### §I.1-DETAIL.3 — Block `roles`

#### Role `store_manager`

- **`allowed_tables`:** Whitelist bảng SQL — PolicyEngine + SqlGateway enforce.
- **`denied_columns`:** Blacklist cột nhạy cảm (SPPRICE, cogs, PASSCODE, …).
- **`store_filter_required`:** true → bắt buộc `store_id IN (...)` predicate.
- **`tool_grants`:** Pattern MCP/tool ACL, ví dụ `tool:*`.
- **`allowed_functions`:** SQL function whitelist pattern `function:*`.
- **denied_columns:** SPPRICE, LASTSPPR, cogs, gross_profit, free_cogs, value_onhand, PASSCODE, PERSON_ID.
- **store_filter_required:** `true` — row-level security theo store_ids từ AUTH.

#### Role `hq_analyst`

- **`allowed_tables`:** Whitelist bảng SQL — PolicyEngine + SqlGateway enforce.
- **`denied_columns`:** Blacklist cột nhạy cảm (SPPRICE, cogs, PASSCODE, …).
- **`store_filter_required`:** true → bắt buộc `store_id IN (...)` predicate.
- **`tool_grants`:** Pattern MCP/tool ACL, ví dụ `tool:*`.
- **`allowed_functions`:** SQL function whitelist pattern `function:*`.
- **denied_columns:** `[]` — full column access trong allowed_tables.
- **store_filter_required:** `false` — HQ xem cross-store.

### §I.1-DETAIL.4 — Danh sách bảng HQ (`_HQ_TABLES`)

- `STRANS` — bảng #1 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `PMTRANS` — bảng #2 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `TRANSHDR` — bảng #3 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `TRANSHDR_ARC` — bảng #4 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `CRDTRANS` — bảng #5 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `CRDTRANS_ARC` — bảng #6 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `CRDTRANS_TMP` — bảng #7 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `STRANS_TMP` — bảng #8 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `SUSPEND` — bảng #9 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `CASH_ST` — bảng #10 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `CTRANS` — bảng #11 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `CUSTOMER` — bảng #12 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `CSCARD` — bảng #13 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `CRD_INFO` — bảng #14 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `CUSTHIST` — bảng #15 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `CustSumm` — bảng #16 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `SKU_DEF` — bảng #17 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `PLU` — bảng #18 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `BARCODE` — bảng #19 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `ASSOLST` — bảng #20 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `ASSO_INF` — bảng #21 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `SUPPLIER` — bảng #22 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `PARTNER` — bảng #23 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `HISRTPR` — bảng #24 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `HISSPPR` — bảng #25 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `RDISCINF` — bảng #26 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `STK_DTL` — bảng #27 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `ST_ORDER` — bảng #28 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `INV_HDR` — bảng #29 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `INV_ISS` — bảng #30 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `PMCRDINF` — bảng #31 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `PMCRDSTK` — bảng #32 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `PMCRDISS` — bảng #33 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `PMCRDRCV` — bảng #34 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `ACCOUNT` — bảng #35 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `DEBT` — bảng #36 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `sku_activity` — bảng #37 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `WebRpt_sales_sku_daily` — bảng #38 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `WebRpt_inventory_daily` — bảng #39 trong grant HQ; kiểm tra data_dictionary tương ứng.
- `WebRpt_rfm_snapshot` — bảng #40 trong grant HQ; kiểm tra data_dictionary tương ứng.

### §I.1-DETAIL.5 — Danh sách bảng Store (`_STORE_TABLES`)

- `STRANS` — allowed cho store_manager; có thể thiếu cột denied.
- `PMTRANS` — allowed cho store_manager; có thể thiếu cột denied.
- `TRANSHDR` — allowed cho store_manager; có thể thiếu cột denied.
- `CRDTRANS` — allowed cho store_manager; có thể thiếu cột denied.
- `CUSTOMER` — allowed cho store_manager; có thể thiếu cột denied.
- `CSCARD` — allowed cho store_manager; có thể thiếu cột denied.
- `CustSumm` — allowed cho store_manager; có thể thiếu cột denied.
- `CUSTHIST` — allowed cho store_manager; có thể thiếu cột denied.
- `SKU_DEF` — allowed cho store_manager; có thể thiếu cột denied.
- `BARCODE` — allowed cho store_manager; có thể thiếu cột denied.
- `PLU` — allowed cho store_manager; có thể thiếu cột denied.
- `SUPPLIER` — allowed cho store_manager; có thể thiếu cột denied.
- `WebRpt_sales_sku_daily` — allowed cho store_manager; có thể thiếu cột denied.
- `WebRpt_inventory_daily` — allowed cho store_manager; có thể thiếu cột denied.
- `WebRpt_rfm_snapshot` — allowed cho store_manager; có thể thiếu cột denied.

### §I.1-DETAIL.6 — Ánh xạ config → code consumer

| Config prefix | Module | Usage |
|---------------|--------|-------|
| `pipeline.*` | `SupermarketAnalysisPipeline` | Retry loops, deadline, IV steps |
| `clarification.*` | `ClarificationCoordinator` | Bridge + hard enforce |
| `rag.*` | `SchemaRetriever, clarify RAG` | top_k, min_score |
| `budget.*` | `BudgetGuard, SessionBudgetTracker` | Per-agent caps |
| `policy.*` | `PolicyEngine` | SQL validation rules |
| `artifacts.*` | `ArtifactStore` | Parquet paths, TTL cleanup |
| `stm.*` | `RedisSTMStore` | Session/workflow TTL |
| `data_sources.*` | `SqlGateway shard resolver` | DSN per db1/db2 |
| `roles.*` | `build_permissions_snapshot, PermissionSet` | ACL at login + pipeline |

### §I.1-DETAIL.7 — Hướng dẫn tuning production

- **Tăng max_sql_retries:** Khi false negative policy; watch latency.
- **Giảm max_rows:** Bảo vệ SQL Server; trade-off với analyst completeness.
- **Tăng workflow_stale_ttl:** User để tab lâu; risk memory STM.
- **Giảm agent_caps.III:** Risk agent hay loop — cap sớm.
- **artifacts.ttl_days:** Disk pressure — cron cleanup_artifacts.
- **clarification.bridge_min_confidence:** UX vs accuracy trade-off.


