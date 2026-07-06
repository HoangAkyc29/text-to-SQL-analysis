# Giới thiệu và kiến trúc tổng thể

Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) (dòng 44–141).

← [Mục lục docs2](README.md)

---

# Phần A — Giới thiệu và bối cảnh nghiệp vụ

## §A.1 Bài toán mà hệ thống giải quyết

Hệ thống cho phép người dùng nội bộ siêu thị (ví dụ: quản lý cửa hàng, phân tích HQ) đặt câu hỏi bằng ngôn ngữ tự nhiên về dữ liệu kinh doanh: doanh thu, VIP, tồn kho, sản phẩm, xu hướng theo thời gian, so sánh cửa hàng, v.v.

Câu trả lời không chỉ là văn bản: hệ thống có thể chạy SQL readonly trên hai cơ sở dữ liệu analytics (`db1`, `db2`), xuất parquet, chạy phân tích pandas trong sandbox, tạo biểu đồ và file CSV/Excel, rồi tổng hợp lời giải thích cho người dùng.

## §A.2 Ràng buộc nghiệp vụ quan trọng

Dữ liệu kinh doanh nằm trên SQL Server với hai database peer (`RESTORED_DB` / `RESTORED_DB2` tương ứng `db1`/`db2` trong code). Không join cross-database trên SQL Server — join/merge thực hiện ở tầng Agent IV (pandas) sau khi mỗi query chạy trên đúng pool.

Một lượng lớn cột text legacy dùng mã TCVN3; sql-gateway chuyển sang Unicode khi trả kết quả `execute_readonly`.

Quyền truy cập là capability-based RBAC lưu trong AUTH DB (`supermarket_auth`), fail-closed: không resolve được quyền thì từ chối.

## §A.3 Các actor chính

| Actor | Vai trò |
|-------|---------|
| End user | Đăng nhập username/password, nhận JWT, gọi `/chat` |
| chat-gateway | API công khai, orchestrator, pipeline host |
| Agent I | Ingress routing, brief, clarify, synthesize |
| Agent II | Lập kế hoạch SQL |
| Agent III | Rà soát rủi ro SQL |
| Agent IV | Thực thi phân tích trên parquet (runtime hiện tại: executor) |
| sql-gateway | Validate/explain/execute SQL readonly |
| python-sandbox | Tool pandas/plot (in-process trong data-analyst) |
| Redis | Short-term memory phiên |
| MongoDB | Schema docs retrieval, analysis_tools registry |
| AUTH SQL Server | Users, roles, permissions |

## §A.4 Thuật ngữ nội bộ

**Brief (`AnalysisBrief`):** Cấu trúc mô tả ý định phân tích — intent, metrics, dimensions, filters, time_range, output_format, external_sources.

**Pipeline:** `SupermarketAnalysisPipeline` trong `project_core.orchestration.pipeline` — state machine điều phối II→III→execute→IV.

**PermissionsSnapshot:** Ảnh chụp quyền tại thời điểm chạy — allowed_tables, denied_columns, tool_grants, allowed_functions, store_ids.

**SqlAclContext:** Đóng gói ACL truyền xuống sql-gateway.

**Trace ID / Analysis ID:** Định danh theo dõi một lần chạy phân tích trong workflow.

---

# Phần B — Kiến trúc tổng thể

## §B.1 Sơ đồ luồng logic (mô tả văn bản)

```
[Browser/Client]
    | POST /auth/login
    v
[chat-gateway:18300] --JWT--> [AUTH DB]
    | POST /chat + Bearer
    v
[ChatOrchestrator]
    | HTTP POST /run
    v
[Agent I:18201] --ingress--> brief + route
    |
    v (route=analysis)
[SupermarketAnalysisPipeline]
    |-- HTTP --> [Agent II:18202] plan SQL
    |-- PolicyEngine (local)
    |-- HTTP --> [Agent III:18203] risk review
    |-- HTTP --> [sql-gateway:18101] execute_readonly
    |-- HTTP --> [Agent IV:18204] analyze_datasets
    |-- HTTP --> [Agent I] synthesize (optional)
    v
[ChatResponse] --> user
```

## §B.2 Phân lớp (layering)

| Lớp | Thành phần | Trách nhiệm |
|-----|------------|-------------|
| Edge | Caddy (prod overlay), chat-gateway FastAPI | TLS, auth user, API |
| Orchestration | ChatOrchestrator, Pipeline | State machine, budget, clarify |
| Agent services | I, II, III, IV HTTP apps | Quyết định theo mode (LLM hoặc executor) |
| Domain | project_core.domain.* | Brief, policy, analysis, ACL |
| Infrastructure | redis_store, mongo_factory, auth_internal | Kết nối ngoài |
| MCP/Data | sql-gateway, python-sandbox | SQL và pandas |
| Config | project.yaml, models.yaml, platform-supermarket.yaml | Khai báo tĩnh |

## §B.3 Giao tiếp giữa các service

Production dùng `PLATFORM_TRANSPORT=http`. `HttpAgentInvoker` và `HttpSqlGatewayClient` trong `chat_gateway.clients` gọi REST. Header `Authorization: Bearer {INTERNAL_SERVICE_TOKEN}` khi `REQUIRE_INTERNAL_AUTH=1`.

Mỗi agent expose `POST /run` nhận `AgentRequest` (session_id, actor_id, message, metadata).

## §B.4 Điểm tập trung logic so với agent boundary

Phần lớn logic nghiệp vụ nằm trong `packages/project-core`, không trong từng agent package. Agents I–III gọi OpenRouter LLM trong `service.decide()`. Agent IV gọi `analyze_datasets()` — không LLM trong service. Pipeline gọi thêm `decompose_brief`, `build_execution_plan`, `recipe_selector` (có LLM) trước khi invoke IV.

---

