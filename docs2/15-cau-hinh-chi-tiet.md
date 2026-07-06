# Cấu hình chi tiết (project, models, platform)

Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) (dòng 29184–29692).

← [Mục lục docs2](README.md)

---

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

### §I.1-DETAIL.8 — Giải thích từng bảng HQ (domain)

| Bảng | Domain | Ghi chú pipeline |
|------|--------|------------------|
| `STRANS` | Giao dịch bán hàng line-item | Shard `STRANS_YYYYMM`; store filter store_manager |
| `PMTRANS` | Thanh toán | Liên kết TRANSHDR; TRANS_CODE 221/008 |
| `TRANSHDR` | Header hóa đơn | Join STRANS; ARC variant archive |
| `CRDTRANS` | Thẻ tín dụng / loyalty | Denied cols store_manager ít hơn HQ |
| `CUSTOMER` | Master khách hàng | PII — cột PASSCODE denied store |
| `SKU_DEF` / `PLU` / `BARCODE` | Master sản phẩm | Schema retrieval ưu tiên |
| `WebRpt_sales_sku_daily` | Aggregate doanh thu | Pre-aggregated — analyst hay dùng |
| `WebRpt_inventory_daily` | Tồn kho ngày | Không expose value_onhand store |
| `WebRpt_rfm_snapshot` | RFM segmentation | Marketing analytics |
| `STK_DTL` / `ST_ORDER` | Kho / đặt hàng | HQ only trong `_HQ_TABLES` |
| `INV_HDR` / `INV_ISS` | Kiểm kê | HQ inventory ops |
| `PMCRD*` | Thẻ PM | Payment card stock/issue/receive |
| `ACCOUNT` / `DEBT` | Công nợ | Finance — HQ analyst |
| `sku_activity` | Hoạt động SKU | Web/reporting derived |

### §I.1-DETAIL.9 — `roles.store_manager.denied_columns` chi tiết

| Cột | Lý do deny |
|-----|------------|
| `SPPRICE`, `LASTSPPR` | Giá mua / supplier price — margin sensitive |
| `cogs`, `gross_profit`, `free_cogs` | COGS / lợi nhuận — chỉ HQ |
| `value_onhand` | Giá trị tồn kho tổng |
| `PASSCODE`, `PERSON_ID` | PII / auth |

PolicyEngine + SqlGateway double-enforce: YAML roles + AUTH DB seed (`004_permissions.sql`).

### §I.1-DETAIL.10 — `data_sources` và shard resolver

- **`db1`**: primary analytics — `ANALYTICS_DB_DSN`; logical `STRANS` → physical `STRANS_202504` etc.
- **`db2`**: secondary — `ANALYTICS_DB_DSN_2`; optional cho cross-DB (hiếm).
- **Resolver:** `project_core.domain.schema.shard_resolver` chọn shard theo date range trong brief.
- **Test:** `test_shard_resolver.py`, `test_live_sql.py` (optional CI).

### §I.1-DETAIL.11 — Fail-closed grants dev (`ALLOW_DEV_AUTH=1`)

Khi dev auth bật, pipeline đọc `roles` từ YAML thay vì AUTH DB. **Bắt buộc** mirror seed SQL — nếu lệch, test ACL (`test_sql_gateway_acl_enforcement.py`) fail. Production: `ALLOW_DEV_AUTH=0`, permissions từ JWT + AUTH DB only.

### §I.1-DETAIL.12 — Quick reference YAML path → Python attribute

| YAML path | Python (`ProjectConfig`) |
|-----------|--------------------------|
| `pipeline.max_sql_retries` | `config.pipeline.max_sql_retries` |
| `budget.agent_caps.III` | `config.budget.agent_caps["III"]` |
| `roles.hq_analyst.allowed_tables` | list resolved từ anchor `*hq_tables` |
| `artifacts.base_dir` | `Path(config.artifacts.base_dir)` |

Loader: `packages/project-core/src/project_core/config/loader.py` — merge với env overrides nếu có trong tương lai.


## §I.2-DETAIL — models.yaml profiles

> **File:** `config/models.yaml` — mapping agent role → LLM profile → OpenRouter model.

### §I.2-DETAIL.1 — agent_profiles mapping

| Key | Profile | Agent |
|-----|---------|-------|
| `default_profile` | `openrouter_mimo` | Fallback khi agent_profiles không chỉ định. |
| `agent_profiles.router` | `openrouter_mimo` | Agent I conversational-router. |
| `agent_profiles.sql_planner` | `openrouter_mimo` | Agent II SQL planning. |
| `agent_profiles.risk_reviewer` | `openrouter_fast` | Agent III — model nhanh, structured JSON. |
| `agent_profiles.analyst` | `openrouter_mimo` | Agent IV text analysis. |
| `agent_profiles.analyst_vision` | `openrouter_vision` | IV khi payload có chart/image. |
| `agent_profiles.embed` | `openrouter_embed` | Embedding RAG — text-embedding-3-small. |

### §I.2-DETAIL.2 — profiles definition

| Profile | provider | model_id | vision | max_tokens | temp | embed_dims | Ghi chú |
|---------|----------|----------|--------|------------|------|------------|---------|
| `openrouter_mimo` | openrouter | xiaomi/mimo-v2.5 | true | 4096 | 0.5 | — | General + vision capable |
| `openrouter_fast` | openrouter | google/gemini-2.0-flash-001 | false | 4096 | 0.5 | — | Fast risk review |
| `openrouter_vision` | openrouter | xiaomi/mimo-v2.5 | true | 4096 | 0.5 | — | Explicit vision tasks |
| `openrouter_embed` | openrouter | openai/text-embedding-3-small | false | — | — | 1536 | RAG embeddings |

### §I.2-DETAIL.3 — Env và runtime
- **API key:** `OPENROUTER_API_KEY` (hoặc legacy `openroute_api_key`) — `BaseAgentService.has_llm()`.
- **Loader:** `project_core` đọc models.yaml; `OpenAICompatibleProvider` dùng profile params.
- **Stub test:** `ALLOW_LLM_STUB=1` trong conftest bypass real LLM.
- **Đổi model prod:** sửa `model_id` trong profile; không cần redeploy agent code nếu API compatible.
### §I.2-DETAIL.4 — Chọn profile theo workload
| Workload | Khuyến nghị | Lý do |
|----------|-------------|-------|
| SQL generation | mimo | Cân bằng reasoning + cost |
| Risk JSON schema | fast (Gemini Flash) | Latency thấp, output ngắn |
| Long report | mimo + tăng max_tokens | Narrative quality |
| Chart analysis | vision | supports_vision=true |
| Schema RAG | embed | 1536-dim vectors |

## §I.3-DETAIL — platform-supermarket.yaml

> **File:** `platform-supermarket.yaml` (repo root) — wiring agents + MCP + memory cho deployment supermarket.

### §I.3-DETAIL.1 — memory block

```yaml
memory:
  stm:
    backend: redis
    url_env: REDIS_URL
  ltm:
    backend: mongodb
    uri_env: MONGODB_URI
    db_name: supermarket_agent
  checkpoint_db_path: ./data/checkpoints.db
```
| Khóa | Giá trị | Consumer |
|------|---------|----------|
| stm.backend | redis | `build_stm` → session + workflow STM |
| stm.url_env | REDIS_URL | Docker compose service redis |
| ltm.backend | mongodb | Case studies, feedback loop indexer |
| ltm.uri_env | MONGODB_URI | `FeedbackLoop`, LTM recall |
| ltm.db_name | supermarket_agent | Database name Mongo |
| checkpoint_db_path | ./data/checkpoints.db | SQLite per-agent checkpoint |
### §I.3-DETAIL.2 — mcp_servers block

**sql-gateway:**
- prefix: `sql` — tool names namespaced `sql_*`.
- transport: `sse` — remote HTTP Server-Sent Events.
- url_env: `SQL_GATEWAY_URL` (default port 18101).
- command/args: fallback local `uv run sql-gateway`.
**python-sandbox:**
- prefix: `sandbox`.
- transport: `stdio` — subprocess MCP.
- command: `uv`, args: `["run", "python-sandbox"]`.
**Tool ownership note:** Pipeline executes tools — agents have `mcp_servers: []`.
### §I.3-DETAIL.3 — agents block

| Agent key | capabilities | endpoint_env | skill | factory |
|-----------|--------------|--------------|-------|---------|
| `conversational-router` | router, ingress, synthesize, clarification_bridge | `AGENT_I_URL` | `router` | `conversational_router.service:build_service` |
| `sql-planner` | sql_plan, clarify | `AGENT_II_URL` | `sql_planner` | `sql_planner.service:build_service` |
| `risk-reviewer` | risk_review | `AGENT_III_URL` | `risk_reviewer` | `risk_reviewer.service:build_service` |
| `data-analyst` | analytics | `AGENT_IV_URL` | `analyst` | `data_analyst.service:build_service` |

### §I.3-DETAIL.4 — orchestration block

```yaml
orchestration:
  type: pipeline
  entry: conversational-router
```
Supermarket dùng **pipeline-centric** architecture — `type: pipeline` không phải full graph DAG.
Entry agent I; thực tế `SupermarketAnalysisPipeline` trong project-core điều phối II→III→IV.
`GraphOrchestrator` available qua CLI nhưng không phải hot path chat-gateway.
### §I.3-DETAIL.5 — Env matrix
| Biến env | Mặc định / ví dụ | Service |
|----------|------------------|---------|
| PLATFORM_CONFIG | platform-supermarket.yaml | All agents app.py |
| REDIS_URL | redis://localhost:6379 | STM |
| MONGODB_URI | mongodb://.../supermarket_agent | LTM, feedback |
| SQL_GATEWAY_URL | http://localhost:18101 | MCP sql tools |
| AGENT_I_URL … AGENT_IV_URL | http://localhost:1820x | HTTP A2A |

