# Biến môi trường chi tiết (§J.1)

Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) (dòng 26417–28212).

← [Mục lục docs2](README.md)

---

## §J.1 — Từng biến môi trường (chi tiết)

Phụ lục này mô tả **từng biến** xuất hiện trong `.env.example` (và một số biến liên quan
được compose hoặc mã nguồn đọc trực tiếp). Nội dung được rút ra từ grep mã nguồn Python/YAML
và file compose — không sao chép từ tài liệu khác trong `docs/`.

Cấu trúc mỗi mục:

1. Tên và giá trị mặc định trong repo.
2. Dịch vụ nào đọc biến khi khởi động hoặc xử lý request.
3. File tham chiếu cụ thể.
4. Khác biệt prod vs dev.
5. Rủi ro bảo mật.
6. Triệu chứng khi thiếu/sai.
7. Cách Docker Compose truyền biến (base vs prod overlay).

---

### §J.1.0 — Nhóm biến theo chức năng

| Nhóm | Biến |
|------|------|
| LLM | OPENROUTER_API_KEY, ALLOW_LLM_STUB |
| Hạ tầng session/RAG | REDIS_URL, MONGODB_URI, MONGODB_CONNECT_TIMEOUT_MS |
| URL dịch vụ | SQL_GATEWAY_URL, AGENT_I_URL … AGENT_IV_URL, CHAT_GATEWAY_URL |
| SQL kinh doanh (readonly) | ANALYTICS_DB_DSN, ANALYTICS_DB_DSN_2 |
| SQL xác thực | AUTH_DB_DSN |
| JWT / auth người dùng | JWT_SECRET, REQUIRE_PROD_AUTH, ALLOW_DEV_AUTH |
| Auth nội bộ gateway↔agents | REQUIRE_INTERNAL_AUTH, INTERNAL_SERVICE_TOKEN |
| OAuth (tùy chọn) | OAUTH_PROVIDER, OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, OAUTH_REDIRECT_URI, AZURE_TENANT_ID |
| Runner / transport | PLATFORM_TRANSPORT |
| Seed mật khẩu AUTH DB | AUTH_SEED_*_PASSWORD (3 biến) |
| Tuning vận hành | LOG_LEVEL, AUTH_PERMISSIONS_CACHE_TTL, SANDBOX_MAX_*, SQL_GATEWAY_MAX_CONCURRENT, SQL_AUDIT_LOG_PATH |
| Prod overlay infra | REDIS_PASSWORD, MONGO_ROOT_USER, MONGO_ROOT_PASSWORD, PUBLIC_DOMAIN, TLS_EMAIL |
| Dev-only (không trong .env.example chính) | SQL_GATEWAY_INPROCESS |
| Compose runtime ports | AGENT_HTTP_PORT, CHAT_GATEWAY_PORT, SQL_GATEWAY_HTTP_PORT |
| Đường dẫn làm việc | AGENT_ROOT_DIR |

Tất cả container ứng dụng trong `docker-compose.yaml` khai báo `env_file: .env`, nghĩa là
biến không bị override trong block `environment:` vẫn được nạp từ file `.env` trên host.

---

#### §J.1.1 — `OPENROUTER_API_KEY`

**Tên biến:** `OPENROUTER_API_KEY`

**Giá trị mặc định (khi không set trong shell):** Không có — bắt buộc khi gọi LLM thật (trừ ALLOW_LLM_STUB=1 hoặc OPENAI_API_KEY).

**Dịch vụ / thành phần đọc biến:**
- chat-gateway (pipeline gọi agents qua HTTP)
- conversational-router (Agent I)
- sql-planner (Agent II)
- risk-reviewer (Agent III)
- data-analyst (Agent IV)
- project-core: OpenRouterClient, EmbeddingClient
- libs/agent-core: OpenAICompatibleProvider, openai_embeddings
- libs/platform-core: BaseAgentService.has_llm()

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `packages/project-core/src/project_core/config/loader.py`
- `libs/agent-core/src/agent_core/capabilities/models/openai_compatible.py`
- `libs/agent-core/src/agent_core/capabilities/retrieval/openai_embeddings.py`
- `libs/platform-core/src/platform_core/service/base.py`

**Hành vi production so với development:**
- Production: ALLOW_LLM_STUB=0; key bắt buộc cho mọi bước reasoning LLM.
- Development: ALLOW_LLM_STUB=1 cho phép bỏ qua key — agents dùng heuristic cố định.
- Alias legacy `openroute_api_key` vẫn đọc được nhưng warnings.warn deprecation.

**Ghi chú bảo mật:**
- Không commit vào git; dùng secret manager trên prod.
- Key có quyền billing — giới hạn quota trên dashboard OpenRouter.
- OPENAI_API_KEY là fallback thứ hai trong agent-core, không có trong .env.example.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- RuntimeError Missing required environment variable khi stub tắt và không có key.
- test_live_llm.py skip khi ALLOW_LLM_STUB=1 hoặc thiếu key.
- Embedding/index schema fail nếu thiếu key khi chạy scripts/index_schema_docs.py.

**Ánh xạ Docker Compose:**
- docker-compose.yaml: env_file .env cho mọi service agent + sql-gateway.
- docker-compose.prod.yaml: không override; vẫn từ .env host.

**Chi tiết bổ sung:**
- Model profile cụ thể nằm trong config/models.yaml, không phải env.

---

#### §J.1.2 — `ALLOW_LLM_STUB`

**Tên biến:** `ALLOW_LLM_STUB`

**Giá trị mặc định (khi không set trong shell):** `0` trong .env.example (production template).

**Dịch vụ / thành phần đọc biến:**
- conversational-router/service.py
- sql-planner/service.py
- risk-reviewer/service.py
- project-core/domain/analysis/decomposer.py
- project-core/domain/analysis/recipe_selector.py
- packages/project-test/conftest.py (setdefault 1 cho test)

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/conversational-router/src/conversational_router/service.py`
- `agents/sql-planner/src/sql_planner/service.py`
- `agents/risk-reviewer/src/risk_reviewer/service.py`
- `packages/project-core/src/project_core/domain/analysis/decomposer.py`
- `packages/project-core/src/project_core/domain/analysis/recipe_selector.py`

**Hành vi production so với development:**
- Prod: phải 0 — mọi quyết định routing/SQL/risk dùng LLM thật.
- Dev: .env.dev.example gợi ý 1 — stub keyword heuristic, không tốn token.
- CI test luôn set 1 trong conftest để không cần API key.

**Ghi chú bảo mật:**
- .env.example ghi rõ Do NOT set ALLOW_LLM_STUB=1 in production.
- Stub không kiểm tra chất lượng output — chỉ phù hợp dev/CI.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- =1: route analysis nếu message chứa từ khóa vip/doanh/bán/chart/điểm.
- =0: gọi OpenRouterClient; lỗi network/API propagate lên pipeline.
- decomposer: use_llm = ALLOW_LLM_STUB != 1.

**Ánh xạ Docker Compose:**
- Không có override compose; đọc từ env_file .env.
- Prod overlay không đụng biến này.

---

#### §J.1.3 — `REDIS_URL`

**Tên biến:** `REDIS_URL`

**Giá trị mặc định (khi không set trong shell):** `redis://localhost:18379/0` (host dev; map port compose 18379→6379).

**Dịch vụ / thành phần đọc biến:**
- chat-gateway: RedisSessionStore (STM — transcript, workflow, clarification)
- project-core/infra/stm/redis_store.py

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `packages/project-core/src/project_core/infra/stm/redis_store.py`
- `agents/chat-gateway/src/chat_gateway/orchestrator.py — khởi tạo RedisSessionStore`
- `agents/chat-gateway/src/chat_gateway/app.py — health_ready ping redis`

**Hành vi production so với development:**
- Dev host: localhost:18379 qua port publish compose.
- Compose base: chat-gateway override REDIS_URL=redis://redis:6379/0 (DNS nội bộ).
- Compose prod: redis://:${REDIS_PASSWORD}@redis:6379/0 — cần REDIS_PASSWORD.

**Ghi chú bảo mật:**
- Base compose: Redis không password — chỉ chấp nhận được trên mạng dev.
- Prod overlay bật --requirepass; URL phải chứa password.
- Session data trong Redis có thể chứa nội dung chat — bảo vệ volume/network.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Sai URL: ConnectionError, /health/ready redis=false.
- Thiếu password trên prod: NOAUTH Authentication required.
- TTL session theo config/project.yaml stm.session_ttl_days, không phải env.

**Ánh xạ Docker Compose:**
- docker-compose.yaml redis service ports 18379:6379.
- chat-gateway environment REDIS_URL=redis://redis:6379/0.
- docker-compose.prod.yaml: command requirepass ${REDIS_PASSWORD}; chat-gateway URL có password.

---

#### §J.1.4 — `MONGODB_URI`

**Tên biến:** `MONGODB_URI`

**Giá trị mặc định (khi không set trong shell):** `mongodb://localhost:18217/supermarket_agent` (host); compose dùng hostname mongodb.

**Dịch vụ / thành phần đọc biến:**
- chat-gateway/orchestrator — FeedbackLoop, HybridMongoRetriever, DomainRuleStore
- sql-planner — hybrid retriever schema docs (mongo_factory)
- project-core/infra/mongo_factory.py
- scripts/index_schema_docs.py

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `packages/project-core/src/project_core/infra/mongo_factory.py`
- `agents/chat-gateway/src/chat_gateway/orchestrator.py`
- `docker-compose.yaml sql-planner + chat-gateway overrides`

**Hành vi production so với development:**
- Dev: không auth, port host 18217.
- Compose base: mongodb://mongodb:27017/supermarket_agent.
- Prod overlay: URI có MONGO_ROOT_USER/PASSWORD và authSource=admin.

**Ghi chú bảo mật:**
- Prod: root creds chỉ áp dụng khi volume mongo mới (MONGO_INITDB_*).
- Đổi password sau khi volume đã init cần thao tác admin Mongo thủ công.
- DB chứa vector RAG, case studies — không public port trên prod.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Sai URI: orchestrator log Mongo/RAG unavailable; feedback=None.
- /health/ready mongo=false khi feedback loop không khởi tạo.
- sql-planner retriever None — giảm chất lượng schema retrieval.

**Ánh xạ Docker Compose:**
- mongodb service ports 18217:27017 (base).
- sql-planner + chat-gateway override MONGODB_URI internal.
- prod: ports [] trên mongodb; credentialed URI trên chat-gateway + sql-planner.

---

#### §J.1.5 — `SQL_GATEWAY_URL`

**Tên biến:** `SQL_GATEWAY_URL`

**Giá trị mặc định (khi không set trong shell):** `http://localhost:18101` khi chạy gateway trên host.

**Dịch vụ / thành phần đọc biến:**
- chat-gateway/clients.py — HttpSqlGatewayClient.base
- platform-supermarket.yaml — url_env cho MCP sql-gateway

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/clients.py`
- `platform-supermarket.yaml`
- `docker-compose.yaml chat-gateway environment`

**Hành vi production so với development:**
- Host dev: localhost:18101.
- Compose: http://sql-gateway:18101 — chỉ reachable trong network compose.
- Prod: không publish port sql-gateway; URL vẫn internal DNS.

**Ghi chú bảo mật:**
- Endpoint chỉ nên reachable từ chat-gateway và mạng nội bộ.
- POST /tools/* yêu cầu internal auth khi REQUIRE_INTERNAL_AUTH=1.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Sai URL: HTTP 404 log check SQL_GATEWAY_URL; circuit breaker mở.
- Gateway down: AgentUnavailableError trong pipeline EXECUTE step.
- SQL_GATEWAY_INPROCESS=1 bỏ qua HTTP — import trực tiếp tools_impl.

**Ánh xạ Docker Compose:**
- sql-gateway ports 18101:18101 (base only).
- chat-gateway sets SQL_GATEWAY_URL=http://sql-gateway:18101.
- prod: sql-gateway ports [] — chỉ chat-gateway gọi được.

---

#### §J.1.6 — `AGENT_I_URL`

**Tên biến:** `AGENT_I_URL`

**Giá trị mặc định (khi không set trong shell):** `http://localhost:18201` — conversational-router.

**Dịch vụ / thành phần đọc biến:**
- chat-gateway HttpAgentInvoker.urls['I']

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/clients.py`
- `agents/conversational-router/src/conversational_router/app.py — AGENT_HTTP_PORT`
- `docker-compose.yaml`

**Hành vi production so với development:**
- Map tới Agent I (ingress, clarify, synthesize).
- Compose: http://conversational-router:18201.
- Prod: internal only, không host port.

**Ghi chú bảo mật:**
- POST /run cần INTERNAL_SERVICE_TOKEN khi auth nội bộ bật.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Sai URL: circuit open, AgentUnavailableError ở bước I.
- /health/ready agents.I=error.

**Ánh xạ Docker Compose:**
- conversational-router AGENT_HTTP_PORT=18201.
- chat-gateway AGENT_I_URL=http://conversational-router:18201.

---

#### §J.1.7 — `AGENT_II_URL`

**Tên biến:** `AGENT_II_URL`

**Giá trị mặc định (khi không set trong shell):** `http://localhost:18202` — sql-planner.

**Dịch vụ / thành phần đọc biến:**
- chat-gateway HttpAgentInvoker.urls['II']

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/clients.py`
- `agents/sql-planner/src/sql_planner/app.py`

**Hành vi production so với development:**
- Agent II sinh/validate SQL plan; cần MONGODB_URI cho schema hybrid retriever.

**Ghi chú bảo mật:**
- Internal auth trên /run giống Agent I.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Unavailable: pipeline kẹt ở bước SQL planning.

**Ánh xạ Docker Compose:**
- sql-planner AGENT_HTTP_PORT=18202; chat-gateway override AGENT_II_URL.

---

#### §J.1.8 — `AGENT_III_URL`

**Tên biến:** `AGENT_III_URL`

**Giá trị mặc định (khi không set trong shell):** `http://localhost:18203` — risk-reviewer.

**Dịch vụ / thành phần đọc biến:**
- chat-gateway HttpAgentInvoker.urls['III']

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/clients.py`
- `agents/risk-reviewer/src/risk_reviewer/app.py`

**Hành vi production so với development:**
- Vòng risk review trước execute SQL.

**Ghi chú bảo mật:**
- Token nội bộ bắt buộc khi REQUIRE_INTERNAL_AUTH=1.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Reject risk → pipeline RISK_REJECT hoặc retry theo max_risk_retries.

**Ánh xạ Docker Compose:**
- risk-reviewer port 18203; compose internal URL.

---

#### §J.1.9 — `AGENT_IV_URL`

**Tên biến:** `AGENT_IV_URL`

**Giá trị mặc định (khi không set trong shell):** `http://localhost:18204` — data-analyst / sandbox.

**Dịch vụ / thành phần đọc biến:**
- chat-gateway HttpAgentInvoker.urls['IV']

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/clients.py`
- `agents/data-analyst/src/data_analyst/app.py`

**Hành vi production so với development:**
- Agent IV chạy phân tích sandbox; volume artifacts shared với chat-gateway.

**Ghi chú bảo mật:**
- Sandbox giới hạn bởi SANDBOX_MAX_ROWS/SECONDS trên python-sandbox tools.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- IV timeout hoặc lỗi → ERROR hoặc partial trong pipeline.

**Ánh xạ Docker Compose:**
- data-analyst volumes supermarket-artifacts; AGENT_IV_URL internal.

---

#### §J.1.10 — `CHAT_GATEWAY_URL`

**Tên biến:** `CHAT_GATEWAY_URL`

**Giá trị mặc định (khi không set trong shell):** `http://localhost:18300` trong .env.example.

**Dịch vụ / thành phần đọc biến:**
- Không có đọc trực tiếp trong mã Python application — dành cho client/UI/scripts bên ngoài
- Caddy prod proxy tới chat-gateway:18300 qua DNS nội bộ, không đọc biến này

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `.env.example dòng 18`
- `deploy/caddy/Caddyfile — reverse_proxy chat-gateway:18300`

**Hành vi production so với development:**
- Dev: client (Postman, frontend) trỏ localhost:18300.
- Prod: user truy cập https://PUBLIC_DOMAIN qua Caddy, không dùng CHAT_GATEWAY_URL trong server.

**Ghi chú bảo mật:**
- Document URL công khai cho team frontend; không phải secret.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Nếu client trỏ sai port: connection refused.
- OAuth OAUTH_REDIRECT_URI mặc định localhost:18300 — phải khớp public URL prod.

**Ánh xạ Docker Compose:**
- chat-gateway CHAT_GATEWAY_PORT=18300 trong container.
- prod: không publish 18300 ra host; chỉ Caddy 80/443.

---

#### §J.1.11 — `ANALYTICS_DB_DSN`

**Tên biến:** `ANALYTICS_DB_DSN`

**Giá trị mặc định (khi không set trong shell):** Trống trong template — bắt buộc khi execute SQL thật trên db1.

**Dịch vụ / thành phần đọc biến:**
- mcp-servers/sql-gateway/tools_impl.py — _connect db1
- config/project.yaml target_dbs.db1.env_dsn
- scripts: explore_db_*, validate_data_dictionary.py

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `mcp-servers/sql-gateway/src/sql_gateway/tools_impl.py`
- `config/project.yaml`
- `docker-compose.yaml sql-gateway environment`

**Hành vi production so với development:**
- ODBC connection string tới SQL Server readonly warehouse db1.
- Host chạy script: DSN trỏ server thật.
- Container sql-gateway: extra_hosts host.docker.internal cho SQL trên host.

**Ghi chú bảo mật:**
- Readonly credential — không dùng user có quyền ghi.
- DSN chứa password — chỉ .env/secret manager.
- TrustServerCertificate=yes phổ biến trên dev SQL.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Thiếu: RuntimeError ANALYTICS_DB_DSN not configured khi target_db=db1.
- test_live_sql.py skip khi không set.
- Pipeline EXECUTE fail policy hoặc gateway error.

**Ánh xạ Docker Compose:**
- sql-gateway environment ANALYTICS_DB_DSN=${ANALYTICS_DB_DSN}.
- prod: không publish port; DSN từ .env host.

---

#### §J.1.12 — `ANALYTICS_DB_DSN_2`

**Tên biến:** `ANALYTICS_DB_DSN_2`

**Giá trị mặc định (khi không set trong shell):** Trống — db2 (RESTORED_DB2) trong config/project.yaml.

**Dịch vụ / thành phần đọc biến:**
- sql-gateway tools_impl _DSN_BY_DB db2
- scripts explore/validate db2

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `mcp-servers/sql-gateway/src/sql_gateway/tools_impl.py`
- `config/project.yaml target_dbs.db2`
- `docker-compose.yaml`

**Hành vi production so với development:**
- Pipeline mặc định execute_readonly target_db db2 trong HttpSqlGatewayClient.
- Hai DSN cho phép tách warehouse logic.

**Ghi chú bảo mật:**
- Tách quyền readonly giữa hai DB nếu cần compliance.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Thiếu khi gọi db2: RuntimeError ANALYTICS_DB_DSN_2 not configured.
- test_sql_gateway có case xóa ANALYTICS_DB_DSN.

**Ánh xạ Docker Compose:**
- Inject song song ANALYTICS_DB_DSN_2 trên sql-gateway service.

---

#### §J.1.13 — `AUTH_DB_DSN`

**Tên biến:** `AUTH_DB_DSN`

**Giá trị mặc định (khi không set trong shell):** Template ODBC tới host.docker.internal:14330 supermarket_auth.

**Dịch vụ / thành phần đọc biến:**
- chat-gateway/auth_store.py — authenticate, load_effective_permissions
- scripts/init_auth_db.py, scripts/seed_auth.py

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/auth_store.py`
- `scripts/init_auth_db.py`
- `scripts/seed_auth.py`

**Hành vi production so với development:**
- Docker: Server=host.docker.internal — SQL Auth trên host Windows.
- Host-native chat-gateway: đổi Server=localhost,14330 hoặc tên instance.
- Uid/Pwd trong DSN phải khớp login SQL đã tạo bởi deploy/sql/auth/.

**Ghi chú bảo mật:**
- Chứa password SQL — rotate định kỳ.
- pyodbc timeout 15s — tránh treo worker.
- Bảng users chứa bcrypt hash — không log password.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Thiếu/empty: RuntimeError AUTH_DB_DSN not configured; login luôn fail.
- authenticate trả None → HTTP 401 invalid credentials.
- permissions None + không ALLOW_DEV_AUTH → 403 permissions_unavailable.

**Ánh xạ Docker Compose:**
- Không có trong compose environment block — từ env_file .env.
- chat-gateway extra_hosts host.docker.internal.

---

#### §J.1.14 — `JWT_SECRET`

**Tên biến:** `JWT_SECRET`

**Giá trị mặc định (khi không set trong shell):** Mặc định code `change-me-in-production` nếu không set.

**Dịch vụ / thành phần đọc biến:**
- chat-gateway/auth.py — issue_token, decode_token, startup validation

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/auth.py`

**Hành vi production so với development:**
- REQUIRE_PROD_AUTH=1: secret >=32 ký tự, không thuộc _WEAK_SECRETS.
- Dev: có thể để default với cảnh báo log.
- Token TTL 8 giờ hardcoded trong issue_token.

**Ghi chú bảo mật:**
- HS256 — một secret cho toàn cluster chat-gateway.
- Rotate secret invalidate mọi JWT đang phát hành.
- Không dùng chung secret với INTERNAL_SERVICE_TOKEN.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Weak + REQUIRE_PROD_AUTH=1: RuntimeError at import auth module — process không start.
- Sai secret khi decode: HTTP 401 invalid_token.
- Missing token + ALLOW_DEV_AUTH=0: 401 missing_token.

**Ánh xạ Docker Compose:**
- Từ env_file .env; không override compose.

---

#### §J.1.15 — `REQUIRE_PROD_AUTH`

**Tên biến:** `REQUIRE_PROD_AUTH`

**Giá trị mặc định (khi không set trong shell):** `1` trong .env.example.

**Dịch vụ / thành phần đọc biến:**
- chat-gateway/auth.py _validate_jwt_secret_at_startup

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/auth.py`

**Hành vi production so với development:**
- =1: enforce JWT_SECRET mạnh trước khi app listen.
- =0: chỉ warn nếu secret yếu — phù hợp dev (.env.dev.example).
- conftest setdefault 0 cho pytest.

**Ghi chú bảo mật:**
- Cờ fail-fast — ngăn deploy prod với secret mặc định.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- =1 + secret yếu: crash startup — container restart loop.
- =0: có thể chạy với change-me-in-production (không an toàn).

**Ánh xạ Docker Compose:**
- Không có trong compose environment; .env only.

---

#### §J.1.16 — `ALLOW_DEV_AUTH`

**Tên biến:** `ALLOW_DEV_AUTH`

**Giá trị mặc định (khi không set trong shell):** `0` production template; `.env.dev.example` gợi ý `1`.

**Dịch vụ / thành phần đọc biến:**
- chat-gateway/auth.py current_user
- chat-gateway/app.py dev-login, orchestrator permissions fallback
- project-core/infra/auth_internal.py
- project-core/domain/access/acl.py

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/auth.py`
- `agents/chat-gateway/src/chat_gateway/app.py`
- `agents/chat-gateway/src/chat_gateway/orchestrator.py`
- `packages/project-core/src/project_core/infra/auth_internal.py`

**Hành vi production so với development:**
- =1: không cần Bearer token — user dev-user hq_analyst.
- =1: POST /auth/dev-login phát JWT tùy chỉnh.
- =1: fallback quyền từ config/project.yaml roles khi AUTH DB fail.
- Prod: phải 0 — mọi /chat cần JWT từ /auth/login.

**Ghi chú bảo mật:**
- .env.example cảnh báo Do NOT set ALLOW_DEV_AUTH=1 in production.
- dev-login bypass toàn bộ password DB.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- =0 + không token: 401 missing_token.
- =0 + AUTH DB down: PermissionsUnavailableError 403.
- Internal auth: ALLOW_DEV_AUTH=1 tắt yêu cầu token nội bộ nếu REQUIRE_INTERNAL_AUTH=0.

**Ánh xạ Docker Compose:**
- env_file .env only.

---

#### §J.1.17 — `REQUIRE_INTERNAL_AUTH`

**Tên biến:** `REQUIRE_INTERNAL_AUTH`

**Giá trị mặc định (khi không set trong shell):** `1` trong .env.example.

**Dịch vụ / thành phần đọc biến:**
- project-core/infra/auth_internal.py
- Tất cả agents /run và sql-gateway /tools/* qua verify_internal_service

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `packages/project-core/src/project_core/infra/auth_internal.py`
- `agents/*/app.py Depends(verify_internal_service)`
- `mcp-servers/sql-gateway/src/sql_gateway/http_app.py`

**Hành vi production so với development:**
- =1: luôn yêu cầu INTERNAL_SERVICE_TOKEN khớp.
- =0: có thể tắt nếu không set token và ALLOW_DEV_AUTH=1.
- Test security_regression set =1.

**Ghi chú bảo mật:**
- Ngăn gọi trực tiếp agent port từ mạng ngoài compose.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- =1 + token trống: HTTP 500 internal_service_token_not_configured.
- Sai token: 401 invalid_service_token.
- chat-gateway clients gửi Bearer + X-Service-Token.

**Ánh xạ Docker Compose:**
- Không override compose; .env.

---

#### §J.1.18 — `INTERNAL_SERVICE_TOKEN`

**Tên biến:** `INTERNAL_SERVICE_TOKEN`

**Giá trị mặc định (khi không set trong shell):** Trống trong template — bắt buộc khi REQUIRE_INTERNAL_AUTH=1.

**Dịch vụ / thành phần đọc biến:**
- auth_internal verify + internal_auth_headers
- chat-gateway/clients HttpAgentInvoker + HttpSqlGatewayClient

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `packages/project-core/src/project_core/infra/auth_internal.py`
- `agents/chat-gateway/src/chat_gateway/clients.py`

**Hành vi production so với development:**
- Shared secret đồng nhất trên chat-gateway và tất cả agents + sql-gateway.
- Dev .env.dev.example để trống khi REQUIRE_INTERNAL_AUTH=0.

**Ghi chú bảo mật:**
- Rotate độc lập JWT_SECRET.
- Độ dài >=32 bytes random; không commit.
- Lộ token = caller có thể invoke /run và /tools.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Mismatch: 401 invalid_service_token giữa gateway và agent.
- Empty + REQUIRE_INTERNAL_AUTH=1: 500 trên mọi invoke nội bộ.

**Ánh xạ Docker Compose:**
- env_file .env; all services đọc cùng giá trị.

---

#### §J.1.19 — `OAUTH_PROVIDER`

**Tên biến:** `OAUTH_PROVIDER`

**Giá trị mặc định (khi không set trong shell):** Mặc định code `local` nếu không set.

**Dịch vụ / thành phần đọc biến:**
- chat-gateway/oauth.py oauth_provider_from_env

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/oauth.py`

**Hành vi production so với development:**
- local: LocalDevOAuthProvider — redirect /auth/dev-login.
- azure: AzureOAuthProvider — Microsoft identity platform.
- .env.example comment: không cần nếu chỉ user/pass AUTH_DB.

**Ghi chú bảo mật:**
- azure cần OAUTH_CLIENT_SECRET — secret app registration.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- local trên prod vô nghĩa nếu ALLOW_DEV_AUTH=0.
- azure + thiếu client_id: authorization URL lỗi từ Microsoft.

**Ánh xạ Docker Compose:**
- env_file .env.

---

#### §J.1.20 — `OAUTH_CLIENT_ID`

**Tên biến:** `OAUTH_CLIENT_ID`

**Giá trị mặc định (khi không set trong shell):** Trống — Azure App Registration Application (client) ID.

**Dịch vụ / thành phần đọc biến:**
- AzureOAuthProvider.__init__

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/oauth.py`

**Hành vi production so với development:**
- Chỉ dùng khi OAUTH_PROVIDER=azure.

**Ghi chú bảo mật:**
- Public identifier — không phải secret nhưng gắn với tenant.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Trống: Microsoft từ chối authorize request.

**Ánh xạ Docker Compose:**
- env_file .env.

---

#### §J.1.21 — `OAUTH_CLIENT_SECRET`

**Tên biến:** `OAUTH_CLIENT_SECRET`

**Giá trị mặc định (khi không set trong shell):** Trống — client secret từ Azure portal.

**Dịch vụ / thành phần đọc biến:**
- AzureOAuthProvider exchange_code

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/oauth.py`

**Hành vi production so với development:**
- Rotate trong Azure khi lộ; cập nhật .env đồng bộ.

**Ghi chú bảo mật:**
- Gửi trong POST token endpoint — chỉ server-side.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Sai secret: HTTP error từ login.microsoftonline.com.

**Ánh xạ Docker Compose:**
- env_file .env.

---

#### §J.1.22 — `OAUTH_REDIRECT_URI`

**Tên biến:** `OAUTH_REDIRECT_URI`

**Giá trị mặc định (khi không set trong shell):** Mặc định `http://localhost:18300/auth/callback`.

**Dịch vụ / thành phần đọc biến:**
- AzureOAuthProvider authorization_url + exchange_code

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/oauth.py`

**Hành vi production so với development:**
- Prod: phải khớp redirect URI đăng ký trong Azure và URL Caddy.
- Dev: localhost:18300.

**Ghi chú bảo mật:**
- Mismatch redirect → Azure error AADSTS50011.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- env_file .env; không có route callback documented trong app.py grep — kiểm tra khi bật SSO.

**Ánh xạ Docker Compose:**
- env_file .env.

---

#### §J.1.23 — `AZURE_TENANT_ID`

**Tên biến:** `AZURE_TENANT_ID`

**Giá trị mặc định (khi không set trong shell):** Mặc định `common` — multi-tenant Microsoft login.

**Dịch vụ / thành phần đọc biến:**
- AzureOAuthProvider tenant trong URL authorize/token

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/oauth.py`

**Hành vi production so với development:**
- Single-tenant doanh nghiệp: set GUID tenant cụ thể.

**Ghi chú bảo mật:**
- common cho phép mọi org Microsoft — cân nhắc hạn chế prod.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Sai tenant: user không thuộc tenant không login được.

**Ánh xạ Docker Compose:**
- env_file .env.

---

#### §J.1.24 — `PLATFORM_TRANSPORT`

**Tên biến:** `PLATFORM_TRANSPORT`

**Giá trị mặc định (khi không set trong shell):** Mặc định `in_process` trong base_runner; .env.example `http`.

**Dịch vụ / thành phần đọc biến:**
- agents/base-runner/src/base_runner/runner.py — AgentPlatform.from_config

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/base-runner/src/base_runner/runner.py`
- `libs/platform-core (AgentPlatform transport resolution)`

**Hành vi production so với development:**
- in_process: gọi agent trong cùng process — dev tooling.
- http: platform gọi agent qua HTTP theo registry.
- Compose stack chính không dùng base-runner — dùng chat-gateway orchestration.

**Ghi chú bảo mật:**
- Không ảnh hưởng docker compose services chính.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Sai transport: platform không resolve endpoint.

**Ánh xạ Docker Compose:**
- Không map trong docker-compose.yaml services list.

---

#### §J.1.25 — `AUTH_SEED_STORE_MANAGER_PASSWORD`

**Tên biến:** `AUTH_SEED_STORE_MANAGER_PASSWORD`

**Giá trị mặc định (khi không set trong shell):** Không set → script seed_auth.py dùng default_password bootstrap (chỉ dev).

**Dịch vụ / thành phần đọc biến:**
- scripts/seed_auth.py — user store.manager

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `scripts/seed_auth.py`

**Hành vi production so với development:**
- Prod: BẮT BUỘC set trước seed; rotate default trong source.
- Dev: có thể rely default St0reManager!Seed#26 — đổi trước go-live.

**Ghi chú bảo mật:**
- Mật khẩu seed không commit; chỉ env lúc chạy script.
- bcrypt rounds=12 per user tại runtime.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Quên set trên prod: user vẫn tạo với password known từ repo script — rủi ro cao.

**Ánh xạ Docker Compose:**
- Chạy trên host, không phải container routine; không trong compose.

---

#### §J.1.26 — `AUTH_SEED_HQ_ANALYST_PASSWORD`

**Tên biến:** `AUTH_SEED_HQ_ANALYST_PASSWORD`

**Giá trị mặc định (khi không set trong shell):** Tương tự — user hq.analyst.

**Dịch vụ / thành phần đọc biến:**
- scripts/seed_auth.py

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `scripts/seed_auth.py`

**Hành vi production so với development:**
- Prod: set unique password mạnh.

**Ghi chú bảo mật:**
- Không share password giữa các seed user.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Default HqAn@lyst!Seed#26 nếu unset.

**Ánh xạ Docker Compose:**
- Host script only.

---

#### §J.1.27 — `AUTH_SEED_ADMIN_PASSWORD`

**Tên biến:** `AUTH_SEED_ADMIN_PASSWORD`

**Giá trị mặc định (khi không set trong shell):** Tương tự — user admin role admin.

**Dịch vụ / thành phần đọc biến:**
- scripts/seed_auth.py

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `scripts/seed_auth.py`

**Hành vi production so với development:**
- Admin có quyền rộng — password phức tạp nhất.

**Ghi chú bảo mật:**
- Không log env khi chạy seed.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Default Adm1n@Superm@rket#26 nếu unset.

**Ánh xạ Docker Compose:**
- Host script only.

---

#### §J.1.28 — `LOG_LEVEL`

**Tên biến:** `LOG_LEVEL`

**Giá trị mặc định (khi không set trong shell):** Mặc định `INFO`.

**Dịch vụ / thành phần đọc biến:**
- libs/commons/logging.py — root logger mọi service dùng get_logger

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `libs/commons/src/commons/logging.py`

**Hành vi production so với development:**
- DEBUG: verbose trên dev — có thể lộ SQL hash/metadata.
- WARNING/ERROR prod để giảm noise.

**Ghi chú bảo mật:**
- DEBUG có thể in payload nhạy cảm nếu code log thêm sau này.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Typo level: Python fallback có thể không set đúng — dùng INFO/DEBUG/WARNING/ERROR.

**Ánh xạ Docker Compose:**
- env_file .env tất cả containers.

---

#### §J.1.29 — `AUTH_PERMISSIONS_CACHE_TTL`

**Tên biến:** `AUTH_PERMISSIONS_CACHE_TTL`

**Giá trị mặc định (khi không set trong shell):** Mặc định `60` (giây).

**Dịch vụ / thành phần đọc biến:**
- chat-gateway/auth_store.py _PERM_CACHE_TTL

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/auth_store.py`

**Hành vi production so với development:**
- Cache per-process in-memory — không shared giữa replicas.
- Giảm TTL khi vừa đổi quyền trong AUTH DB cần hiệu lực nhanh.

**Ghi chú bảo mật:**
- TTL cao: user bị revoke vẫn dùng được tối đa TTL giây.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- =0 hoặc âm: cache hết hạn ngay hoặc hành vi lạ — nên giữ 30-120.

**Ánh xạ Docker Compose:**
- env_file .env chat-gateway.

---

#### §J.1.30 — `SANDBOX_MAX_ROWS`

**Tên biến:** `SANDBOX_MAX_ROWS`

**Giá trị mặc định (khi không set trong shell):** Mặc định `200000`.

**Dịch vụ / thành phần đọc biến:**
- mcp-servers/python-sandbox/tools_impl.py load_dataset

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `mcp-servers/python-sandbox/src/python_sandbox/tools_impl.py`

**Hành vi production so với development:**
- Giới hạn hàng đọc parquet/csv trong sandbox Agent IV.
- Prod: có thể hạ để giảm RAM container data-analyst.

**Ghi chú bảo mật:**
- Tránh OOM khi dataset lớn.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Vượt cap: dataframe head truncate silently — kết quả phân tích thiếu hàng.

**Ánh xạ Docker Compose:**
- data-analyst container env_file; không override compose.

---

#### §J.1.31 — `SANDBOX_MAX_SECONDS`

**Tên biến:** `SANDBOX_MAX_SECONDS`

**Giá trị mặc định (khi không set trong shell):** Mặc định `30`.

**Dịch vụ / thành phần đọc biến:**
- python-sandbox tools_impl subprocess timeout

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `mcp-servers/python-sandbox/src/python_sandbox/tools_impl.py`

**Hành vi production so với development:**
- Subprocess runner_child.py kill sau N giây.

**Ghi chú bảo mật:**
- Ngăn code LLM sinh ra chạy vô hạn.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Timeout: sandbox step error trong pipeline.

**Ánh xạ Docker Compose:**
- env_file data-analyst.

---

#### §J.1.32 — `SQL_GATEWAY_MAX_CONCURRENT`

**Tên biến:** `SQL_GATEWAY_MAX_CONCURRENT`

**Giá trị mặc định (khi không set trong shell):** Mặc định `8`.

**Dịch vụ / thành phần đọc biến:**
- sql-gateway tools_impl _semaphore

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `mcp-servers/sql-gateway/src/sql_gateway/tools_impl.py`

**Hành vi production so với development:**
- Giới hạn query ODBC đồng thời trên sql-gateway.
- Tăng khi warehouse chịu tải và có pool connection.

**Ghi chú bảo mật:**
- Quá cao: có thể làm quá tải SQL Server readonly.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Chờ semaphore — latency tăng, không fail ngay.

**Ánh xạ Docker Compose:**
- sql-gateway env_file .env.

---

#### §J.1.33 — `MONGODB_CONNECT_TIMEOUT_MS`

**Tên biến:** `MONGODB_CONNECT_TIMEOUT_MS`

**Giá trị mặc định (khi không set trong shell):** Mặc định `2000`.

**Dịch vụ / thành phần đọc biến:**
- chat-gateway/orchestrator MongoClient serverSelectionTimeoutMS

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/orchestrator.py`

**Hành vi production so với development:**
- Fail nhanh khi mongo chưa ready — tránh treo startup.
- Prod overlay depends_on healthy — có thể tăng nhẹ.

**Ghi chú bảo mật:**
- Quá thấp trên mạng chậm: false negative RAG unavailable.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Timeout: exception trong try → feedback None.

**Ánh xạ Docker Compose:**
- chat-gateway env_file.

---

#### §J.1.34 — `SQL_AUDIT_LOG_PATH`

**Tên biến:** `SQL_AUDIT_LOG_PATH`

**Giá trị mặc định (khi không set trong shell):** Mặc định project_core.paths.AUDIT_LOG (data/state/audit.jsonl).

**Dịch vụ / thành phần đọc biến:**
- project-core/domain/audit/logger.py AuditLogger

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `packages/project-core/src/project_core/domain/audit/logger.py`
- `project-core/paths.py AUDIT_LOG`

**Hành vi production so với development:**
- Pipeline chat-gateway ghi sql_execute/sql_explain events JSONL.
- Compose mount supermarket-state:/app/data/state.

**Ghi chú bảo mật:**
- File chứa sql hash, actor_id — bảo vệ volume.
- Không ghi full SQL text — chỉ hash 16 hex.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- OSError khi ghi: silently pass — mất audit trail.
- Sai path read-only FS: không tạo được file.

**Ánh xạ Docker Compose:**
- Volume supermarket-state trên chat-gateway.

---

#### §J.1.35 — `REDIS_PASSWORD`

**Tên biến:** `REDIS_PASSWORD`

**Giá trị mặc định (khi không set trong shell):** Trống — chỉ dùng docker-compose.prod.yaml.

**Dịch vụ / thành phần đọc biến:**
- redis-server --requirepass
- chat-gateway REDIS_URL interpolation

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `docker-compose.prod.yaml redis command + healthcheck`
- `docker-compose.prod.yaml chat-gateway REDIS_URL`

**Hành vi production so với development:**
- Bắt buộc khi chạy prod overlay.
- Dev base compose không dùng.

**Ghi chú bảo mật:**
- Password trong URL Redis — tránh log connection string.
- Đổi password cần restart redis + update .env + chat-gateway.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Thiếu trên prod: redis start fail hoặc NOAUTH.
- Sai password: chat-gateway không ping redis.

**Ánh xạ Docker Compose:**
- Substituted ${REDIS_PASSWORD} trong prod compose only.

---

#### §J.1.36 — `MONGO_ROOT_USER`

**Tên biến:** `MONGO_ROOT_USER`

**Giá trị mặc định (khi không set trong shell):** Trống — MONGO_INITDB_ROOT_USERNAME prod overlay.

**Dịch vụ / thành phần đọc biến:**
- mongodb service environment prod
- MONGODB_URI trên chat-gateway + sql-planner

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `docker-compose.prod.yaml mongodb environment`
- `docker-compose.prod.yaml chat-gateway + sql-planner MONGODB_URI`

**Hành vi production so với development:**
- Chỉ hiệu lực khi volume mongo mới.
- User root admin authSource=admin.

**Ghi chú bảo mật:**
- Root creds mạnh — không dùng cho app trừ khi thiết kế hiện tại.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Volume cũ không có user: init script không chạy lại — mismatch creds.

**Ánh xạ Docker Compose:**
- ${MONGO_ROOT_USER} trong prod compose.

---

#### §J.1.37 — `MONGO_ROOT_PASSWORD`

**Tên biến:** `MONGO_ROOT_PASSWORD`

**Giá trị mặc định (khi không set trong shell):** Trống — cặp với MONGO_ROOT_USER.

**Dịch vụ / thành phần đọc biến:**
- Giống MONGO_ROOT_USER

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `docker-compose.prod.yaml`

**Hành vi production so với development:**
- Rotate: tạo user app riêng là improvement tương lai.
- Hiện tại URI embed root password.

**Ghi chú bảo mật:**
- Lộ password = full read/write mongo.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Auth fail: orchestrator Mongo/RAG unavailable.

**Ánh xạ Docker Compose:**
- prod compose interpolation.

---

#### §J.1.38 — `PUBLIC_DOMAIN`

**Tên biến:** `PUBLIC_DOMAIN`

**Giá trị mặc định (khi không set trong shell):** Mặc định `localhost` trong .env.example.

**Dịch vụ / thành phần đọc biến:**
- Caddyfile {$PUBLIC_DOMAIN} server block
- caddy service environment

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `deploy/caddy/Caddyfile`
- `docker-compose.prod.yaml caddy environment`

**Hành vi production so với development:**
- localhost: cert self-signed — browser warning.
- Domain thật: Let's Encrypt auto qua Caddy.
- Cần DNS public trỏ host và mở 80/443.

**Ghi chú bảo mật:**
- PUBLIC_DOMAIN lộ trong TLS cert — không phải secret nhưng xác định deployment.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Domain sai: cert không match, client TLS error.

**Ánh xạ Docker Compose:**
- prod only — service caddy không có trong base compose; caddy environment PUBLIC_DOMAIN.

---

#### §J.1.39 — `TLS_EMAIL`

**Tên biến:** `TLS_EMAIL`

**Giá trị mặc định (khi không set trong shell):** Mặc định `admin@example.com` — đổi trên prod.

**Dịch vụ / thành phần đọc biến:**
- Caddyfile global email {$TLS_EMAIL}

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `deploy/caddy/Caddyfile`
- `docker-compose.prod.yaml`

**Hành vi production so với development:**
- Let's Encrypt ACME registration email.
- Không ảnh hưởng runtime app logic.

**Ghi chú bảo mật:**
- Email ACME có thể nhận thông báo hết hạn cert — dùng alias ops team.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Email không hợp lệ: LE có thể từ chối rate limit recovery.

**Ánh xạ Docker Compose:**
- caddy environment prod overlay TLS_EMAIL=${TLS_EMAIL}.

---

#### §J.1.40 — `SQL_GATEWAY_INPROCESS`

**Tên biến:** `SQL_GATEWAY_INPROCESS`

**Giá trị mặc định (khi không set trong shell):** Không set (mặc định HTTP client).

**Dịch vụ / thành phần đọc biến:**
- chat-gateway/clients HttpSqlGatewayClient._call

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/clients.py`

**Hành vi production so với development:**
- =1: import sql_gateway.tools_impl trong process chat-gateway — test nhanh.
- Prod: không set — tách process sql-gateway.

**Ghi chú bảo mật:**
- In-process bỏ qua network auth boundary — chỉ dev.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Import fail nếu thiếu dependency sql-gateway trong image chat-gateway.

**Ánh xạ Docker Compose:**
- .env.dev.example comment SQL_GATEWAY_INPROCESS=1.
- test_chat_gateway monkeypatch set 1.

---

#### §J.1.41 — `AGENT_HTTP_PORT`

**Tên biến:** `AGENT_HTTP_PORT`

**Giá trị mặc định (khi không set trong shell):** 18201/18202/18203/18204 tùy agent; base-agent legacy default 8200.

**Dịch vụ / thành phần đọc biến:**
- Mỗi agents/*/app.py uvicorn port
- docker-compose environment per service

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/conversational-router/src/conversational_router/app.py`
- `agents/sql-planner/src/sql_planner/app.py`
- `agents/risk-reviewer/src/risk_reviewer/app.py`
- `agents/data-analyst/src/data_analyst/app.py`
- `docker-compose.yaml`

**Hành vi production so với development:**
- Compose set cố định 1820x khớp AGENT_*_URL.
- Local uv run không qua compose: dùng default trong app.py.

**Ghi chú bảo mật:**
- Port publish ra host trên dev — prod overlay ports [].

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Mismatch port vs URL: connection refused từ chat-gateway.

**Ánh xạ Docker Compose:**
- environment AGENT_HTTP_PORT trên từng agent service.

---

#### §J.1.42 — `CHAT_GATEWAY_PORT`

**Tên biến:** `CHAT_GATEWAY_PORT`

**Giá trị mặc định (khi không set trong shell):** Mặc định `18300`.

**Dịch vụ / thành phần đọc biến:**
- chat-gateway/app.py uvicorn

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `agents/chat-gateway/src/chat_gateway/app.py`
- `docker-compose.yaml`
- `deploy/caddy/Caddyfile reverse_proxy chat-gateway:18300`

**Hành vi production so với development:**
- Container listen 18300; Caddy proxy cùng port nội bộ.

**Ghi chú bảo mật:**
- Prod không expose ra host.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Đổi port phải sync Caddyfile + compose.

**Ánh xạ Docker Compose:**
- environment CHAT_GATEWAY_PORT=18300.

---

#### §J.1.43 — `SQL_GATEWAY_HTTP_PORT`

**Tên biến:** `SQL_GATEWAY_HTTP_PORT`

**Giá trị mặc định (khi không set trong shell):** Mặc định `18101`.

**Dịch vụ / thành phần đọc biến:**
- sql-gateway/http_app.py uvicorn

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `mcp-servers/sql-gateway/src/sql_gateway/http_app.py`
- `docker-compose.yaml sql-gateway environment`

**Hành vi production so với development:**
- Map host 18101 trên dev compose.

**Ghi chú bảo mật:**
- Prod không publish.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Conflict port nếu process khác chiếm 18101.

**Ánh xạ Docker Compose:**
- SQL_GATEWAY_HTTP_PORT=18101 trong sql-gateway service.

---

#### §J.1.44 — `AGENT_ROOT_DIR`

**Tên biến:** `AGENT_ROOT_DIR`

**Giá trị mặc định (khi không set trong shell):** Mặc định Path.cwd() hoặc set bởi base_runner.

**Dịch vụ / thành phần đọc biến:**
- project_core/config/env.py project_root
- project_core/paths.py ROOT
- base_runner __init__ setdefault

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `packages/project-core/src/project_core/config/env.py`
- `packages/project-core/src/project_core/paths.py`
- `agents/base-runner/src/base_runner/runner.py`

**Hành vi production so với development:**
- Xác định vị trí .env, config/, data/.
- Docker: WORKDIR /app — cwd là repo root trong image.

**Ghi chú bảo mật:**
- Sai root: load sai project.yaml hoặc không tìm thấy .env.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- WORKDIR /app trong Dockerfile — thường không cần set env.

**Ánh xạ Docker Compose:**
- Không trong compose environment block.

---

#### §J.1.45 — `openroute_api_key (legacy)`

**Tên biến:** `openroute_api_key (legacy)`

**Giá trị mặc định (khi không set trong shell):** Không có trong .env.example — alias deprecated.

**Dịch vụ / thành phần đọc biến:**
- get_openrouter_api_key, OpenAICompatibleProvider, sample_code

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `packages/project-core/src/project_core/config/loader.py`
- `sample_code/model_calling.py`

**Hành vi production so với development:**
- Chỉ dùng khi chưa migrate sang OPENROUTER_API_KEY.

**Ghi chú bảo mật:**
- Deprecation warning — xóa sau migrate.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Cùng failure mode OPENROUTER_API_KEY.

**Ánh xạ Docker Compose:**
- Không document trong compose.

---

#### §J.1.46 — `OPENAI_API_KEY`

**Tên biến:** `OPENAI_API_KEY`

**Giá trị mặc định (khi không set trong shell):** Không trong .env.example — fallback thứ hai agent-core.

**Dịch vụ / thành phần đọc biến:**
- openai_compatible.py, openai_embeddings.py

**Tham chiếu mã nguồn (đường dẫn tương đối repo):**
- `libs/agent-core/src/agent_core/capabilities/models/openai_compatible.py`

**Hành vi production so với development:**
- Dùng nếu không set OPENROUTER_API_KEY nhưng có OpenAI trực tiếp.

**Ghi chú bảo mật:**
- Billing OpenAI riêng — không mix key trong log.

**Chế độ lỗi / triệu chứng khi cấu hình sai:**
- Thiếu cả hai key: LLM call fail.

**Ánh xạ Docker Compose:**
- env_file nếu set thủ công.

---

### §J.1.47 — Ma trận service × biến môi trường

Bảng dưới tóm tắt **ai đọc gì** khi container khởi động (qua `env_file: .env` + override).

| Service | Biến đọc trực tiếp / quan trọng |
|---------|----------------------------------|
| chat-gateway | REDIS_URL, MONGODB_URI, MONGODB_CONNECT_TIMEOUT_MS, SQL_GATEWAY_URL, AGENT_I–IV_URL, AUTH_DB_DSN, JWT_*, ALLOW_DEV_AUTH, REQUIRE_PROD_AUTH, INTERNAL_*, OPENROUTER (agents), LOG_LEVEL, SQL_AUDIT_LOG_PATH, AUTH_PERMISSIONS_CACHE_TTL |
| sql-gateway | ANALYTICS_DB_DSN, ANALYTICS_DB_DSN_2, SQL_GATEWAY_MAX_CONCURRENT, INTERNAL_*, LOG_LEVEL |
| conversational-router | ALLOW_LLM_STUB, OPENROUTER_API_KEY, AGENT_HTTP_PORT, INTERNAL_* |
| sql-planner | ALLOW_LLM_STUB, MONGODB_URI, OPENROUTER, AGENT_HTTP_PORT, INTERNAL_* |
| risk-reviewer | ALLOW_LLM_STUB, OPENROUTER, AGENT_HTTP_PORT, INTERNAL_* |
| data-analyst | ALLOW_LLM_STUB, OPENROUTER, SANDBOX_MAX_*, AGENT_HTTP_PORT, INTERNAL_* |
| redis (prod) | REDIS_PASSWORD (command line) |
| mongodb (prod) | MONGO_ROOT_USER, MONGO_ROOT_PASSWORD |
| caddy (prod) | PUBLIC_DOMAIN, TLS_EMAIL |

---

### §J.1.48 — Thứ tự nạp biến môi trường

1. Shell export trước khi chạy process có hiệu lực cao nhất.
2. `load_project_env()` gọi `dotenv.load_dotenv(<root>/.env)` — không ghi đè biến đã có trong shell.
3. Docker Compose `environment:` override `env_file` cho cùng tên biến.
4. Một số giá trị mặc định hardcode trong `os.getenv(name, default)` khi cả shell và .env đều thiếu.

File tham chiếu: `packages/project-core/src/project_core/config/env.py`.

Implication cho vận hành:

- Sửa `.env` trên host **không** tự reload container — cần `docker compose up -d` recreate hoặc restart service.
- Test pytest dùng `monkeypatch.setenv` — không đọc .env thật trừ integration có load_project_env.
- `conftest.py` setdefault ALLOW_LLM_STUB=1, ALLOW_DEV_AUTH=1, REQUIRE_PROD_AUTH=0 — test không đại diện prod.

---

### §J.1.49 — Checklist prod tối thiểu (chỉ env)

Trước `docker compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d`:

1. OPENROUTER_API_KEY — set; ALLOW_LLM_STUB=0.
2. ANALYTICS_DB_DSN và ANALYTICS_DB_DSN_2 — ODBC tới warehouse readonly.
3. AUTH_DB_DSN — tới supermarket_auth; đã chạy init_all.sql + seed với AUTH_SEED_*.
4. JWT_SECRET — >=32 ký tự random; REQUIRE_PROD_AUTH=1; ALLOW_DEV_AUTH=0.
5. REQUIRE_INTERNAL_AUTH=1; INTERNAL_SERVICE_TOKEN — random dài, giống nhau mọi service.
6. REDIS_PASSWORD, MONGO_ROOT_USER, MONGO_ROOT_PASSWORD — mạnh, unique.
7. PUBLIC_DOMAIN — FQDN thật; TLS_EMAIL — email ops hợp lệ.
8. Không set SQL_GATEWAY_INPROCESS, ALLOW_DEV_AUTH, ALLOW_LLM_STUB.

---

### §J.1.50 — Luồng auth: biến env tham gia thế nào

```
Client → POST /auth/login (username/password)
         ↓ AUTH_DB_DSN → auth_store.authenticate (bcrypt)
         ↓ JWT_SECRET → issue_token (HS256, 8h)
Client → POST /chat + Authorization Bearer
         ↓ decode JWT; load_effective_permissions (AUTH_DB + AUTH_PERMISSIONS_CACHE_TTL)
         ↓ nếu None và ALLOW_DEV_AUTH=0 → 403 permissions_unavailable
chat-gateway → POST agent/run + INTERNAL_SERVICE_TOKEN
         ↓ verify_internal_service trên agent
chat-gateway → POST sql-gateway/tools/* + token
         ↓ ANALYTICS_DB_DSN(_2) execute readonly
```

---

### §J.1.51 — Góc nhìn vận hành: `chat-gateway`

- Điểm vào duy nhất cho HTTP client (trừ Caddy terminate TLS).
- Khởi tạo RedisSessionStore ngay — phụ thuộc REDIS_URL.
- Khởi tạo Mongo optional — MONGODB_URI + MONGODB_CONNECT_TIMEOUT_MS.
- HttpAgentInvoker đọc AGENT_I_URL … IV_URL lúc __init__ — đổi env cần restart.
- Pipeline SupermarketAnalysisPipeline dùng chung httpx client 120s timeout.
- Volume artifacts + state cho parquet và SQL_AUDIT_LOG_PATH.
- extra_hosts host.docker.internal cho AUTH_DB_DSN tới SQL trên host Windows.

---

### §J.1.52 — Góc nhìn vận hành: `sql-gateway`

- FastAPI /health không cần internal auth.
- Mọi /tools/{name} require verify_internal_service.
- tools_impl đọc DSN env at connection time — có thể đổi DSN sau restart.
- Semaphore SQL_GATEWAY_MAX_CONCURRENT toàn process.
- Rate limit 30 req/phút/actor_id trong explain/execute.
- depends_on redis mongodb trên base compose — redis/mongo không dùng trực tiếp trong tools_impl hiện tại.

---

### §J.1.53 — Góc nhìn vận hành: `conversational-router`

- Agent I — mode ingress/clarify/synthesize/clarification_bridge trong metadata.
- ALLOW_LLM_STUB quyết định heuristic vs OpenRouterClient.
- Không đọc MONGODB_URI trực tiếp trong service.py grep.
- AGENT_HTTP_PORT expose 18201 trên dev.

---

### §J.1.54 — Góc nhìn vận hành: `sql-planner`

- Agent II — SQL generation và validation logic.
- Compose inject MONGODB_URI riêng — schema hybrid retrieval.
- ALLOW_LLM_STUB trả SQL stub cố định cho test.

---

### §J.1.55 — Góc nhìn vận hành: `risk-reviewer`

- Agent III — risk review trước execute.
- Stub mode bỏ qua LLM risk scoring.

---

### §J.1.56 — Góc nhìn vận hành: `data-analyst`

- Agent IV — gọi python-sandbox MCP tools.
- SANDBOX_MAX_ROWS và SANDBOX_MAX_SECONDS đọc trong tools_impl.
- Shared volume supermarket-artifacts với chat-gateway.

---

### §J.1.57 — Tra cứu nhanh triệu chứng × biến

- **Triệu chứng:** Container chat-gateway restart loop ngay khi start → kiểm tra **JWT_SECRET + REQUIRE_PROD_AUTH=1**.
- **Triệu chứng:** 401 missing_token trên /chat → kiểm tra **ALLOW_DEV_AUTH=0 và thiếu Authorization header**.
- **Triệu chứng:** 403 dev_auth_disabled trên /auth/dev-login → kiểm tra **ALLOW_DEV_AUTH không phải 1**.
- **Triệu chứng:** 403 permissions_unavailable → kiểm tra **AUTH_DB_DSN sai hoặc user không có role_permissions**.
- **Triệu chứng:** 500 internal_service_token_not_configured → kiểm tra **REQUIRE_INTERNAL_AUTH=1 nhưng INTERNAL_SERVICE_TOKEN trống**.
- **Triệu chứng:** 401 invalid_service_token giữa services → kiểm tra **Token khác nhau giữa .env các container — recreate all**.
- **Triệu chứng:** NOAUTH redis → kiểm tra **Prod REDIS_URL thiếu :password@ hoặc REDIS_PASSWORD sai**.
- **Triệu chứng:** Mongo/RAG unavailable warning → kiểm tra **MONGODB_URI sai, mongo chưa healthy, hoặc timeout quá ngắn**.
- **Triệu chứng:** ANALYTICS_DB_DSN not configured → kiểm tra **sql-gateway thiếu DSN cho target_db đang gọi**.
- **Triệu chứng:** sql-gateway HTTP 404 → kiểm tra **SQL_GATEWAY_URL sai path hoặc tool name**.
- **Triệu chứng:** Circuit open for agent II → kiểm tra **AGENT_II_URL sai hoặc sql-planner down**.
- **Triệu chứng:** RuntimeError Missing OPENROUTER_API_KEY → kiểm tra **ALLOW_LLM_STUB=0 mà không có key**.
- **Triệu chứng:** Let's Encrypt không cấp cert → kiểm tra **PUBLIC_DOMAIN DNS, port 80/443, TLS_EMAIL**.
- **Triệu chứng:** ODBC login failed AUTH → kiểm tra **AUTH_DB_DSN Uid/Pwd không khớp SQL login**.
- **Triệu chứng:** Seed user password known publicly → kiểm tra **AUTH_SEED_* không set trước seed_auth.py trên prod**.

---

### §J.1.58 — docker-compose.yaml: từng service environment block

- project-base / mcp-base / agent-base: profile docker-bases — không env app.
- redis: image redis:7-alpine; ports 18379:6379; không env; volume supermarket-redis.
- mongodb: image mongo:7; ports 18217:27017; không auth env trên base.
- sql-gateway: env_file .env; environment ANALYTICS_DB_DSN, ANALYTICS_DB_DSN_2, SQL_GATEWAY_HTTP_PORT=18101.
- sql-gateway: ports 18101; extra_hosts host.docker.internal; depends_on redis mongodb.
- conversational-router: env_file .env; AGENT_HTTP_PORT=18201; ports 18201.
- sql-planner: env_file .env; AGENT_HTTP_PORT=18202; MONGODB_URI override internal; depends_on mongodb.
- risk-reviewer: env_file .env; AGENT_HTTP_PORT=18203; ports 18203.
- data-analyst: env_file .env; AGENT_HTTP_PORT=18204; volumes artifacts + attachments.
- chat-gateway: env_file .env; override REDIS_URL, MONGODB_URI, SQL_GATEWAY_URL, AGENT_I–IV_URL.
- chat-gateway: CHAT_GATEWAY_PORT=18300; ports 18300; volumes artifacts, attachments, state.
- chat-gateway: depends_on full agent stack + sql-gateway + redis + mongodb.

---

### §J.1.59 — docker-compose.prod.yaml: delta so với base

- redis: ports []; requirepass REDIS_PASSWORD; healthcheck AUTH ping.
- mongodb: ports []; MONGO_INITDB_ROOT_USERNAME/PASSWORD; healthcheck mongosh ping.
- sql-gateway: ports []; healthcheck HTTP /health; depends_on redis+mongo healthy.
- Tất cả agents: ports [] — không expose ra host.
- sql-planner: MONGODB_URI credentialed với MONGO_ROOT_* authSource=admin.
- chat-gateway: REDIS_URL và MONGODB_URI credentialed; depends_on healthy conditions.
- caddy: NEW service; ports 80+443; PUBLIC_DOMAIN TLS_EMAIL; proxy chat-gateway:18300.
- Volumes thêm: caddy-data, caddy-config cho cert persistence.

---

### §J.1.60 — Nhóm `LLM`: tương tác chéo

Các biến: `OPENROUTER_API_KEY`, `ALLOW_LLM_STUB`.

**OPENROUTER_API_KEY** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa OPENROUTER_API_KEY.
- Prod: sau khi sửa OPENROUTER_API_KEY, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback OPENROUTER_API_KEY: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**ALLOW_LLM_STUB** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa ALLOW_LLM_STUB.
- Prod: sau khi sửa ALLOW_LLM_STUB, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback ALLOW_LLM_STUB: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

---

### §J.1.61 — Nhóm `Session`: tương tác chéo

Các biến: `REDIS_URL`.

**REDIS_URL** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa REDIS_URL.
- Prod: sau khi sửa REDIS_URL, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback REDIS_URL: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

---

### §J.1.62 — Nhóm `RAG`: tương tác chéo

Các biến: `MONGODB_URI`, `MONGODB_CONNECT_TIMEOUT_MS`.

**MONGODB_URI** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa MONGODB_URI.
- Prod: sau khi sửa MONGODB_URI, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback MONGODB_URI: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**MONGODB_CONNECT_TIMEOUT_MS** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa MONGODB_CONNECT_TIMEOUT_MS.
- Prod: sau khi sửa MONGODB_CONNECT_TIMEOUT_MS, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback MONGODB_CONNECT_TIMEOUT_MS: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

---

### §J.1.63 — Nhóm `Routing`: tương tác chéo

Các biến: `AGENT_I_URL`, `AGENT_II_URL`, `AGENT_III_URL`, `AGENT_IV_URL`, `SQL_GATEWAY_URL`.

**AGENT_I_URL** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa AGENT_I_URL.
- Prod: sau khi sửa AGENT_I_URL, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback AGENT_I_URL: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**AGENT_II_URL** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa AGENT_II_URL.
- Prod: sau khi sửa AGENT_II_URL, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback AGENT_II_URL: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**AGENT_III_URL** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa AGENT_III_URL.
- Prod: sau khi sửa AGENT_III_URL, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback AGENT_III_URL: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**AGENT_IV_URL** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa AGENT_IV_URL.
- Prod: sau khi sửa AGENT_IV_URL, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback AGENT_IV_URL: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**SQL_GATEWAY_URL** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa SQL_GATEWAY_URL.
- Prod: sau khi sửa SQL_GATEWAY_URL, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback SQL_GATEWAY_URL: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

---

### §J.1.64 — Nhóm `Data`: tương tác chéo

Các biến: `ANALYTICS_DB_DSN`, `ANALYTICS_DB_DSN_2`.

**ANALYTICS_DB_DSN** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa ANALYTICS_DB_DSN.
- Prod: sau khi sửa ANALYTICS_DB_DSN, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback ANALYTICS_DB_DSN: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**ANALYTICS_DB_DSN_2** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa ANALYTICS_DB_DSN_2.
- Prod: sau khi sửa ANALYTICS_DB_DSN_2, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback ANALYTICS_DB_DSN_2: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

---

### §J.1.65 — Nhóm `Identity`: tương tác chéo

Các biến: `AUTH_DB_DSN`, `JWT_SECRET`, `REQUIRE_PROD_AUTH`, `ALLOW_DEV_AUTH`.

**AUTH_DB_DSN** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa AUTH_DB_DSN.
- Prod: sau khi sửa AUTH_DB_DSN, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback AUTH_DB_DSN: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**JWT_SECRET** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa JWT_SECRET.
- Prod: sau khi sửa JWT_SECRET, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback JWT_SECRET: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**REQUIRE_PROD_AUTH** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa REQUIRE_PROD_AUTH.
- Prod: sau khi sửa REQUIRE_PROD_AUTH, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback REQUIRE_PROD_AUTH: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**ALLOW_DEV_AUTH** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa ALLOW_DEV_AUTH.
- Prod: sau khi sửa ALLOW_DEV_AUTH, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback ALLOW_DEV_AUTH: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

---

### §J.1.66 — Nhóm `Mesh`: tương tác chéo

Các biến: `REQUIRE_INTERNAL_AUTH`, `INTERNAL_SERVICE_TOKEN`.

**REQUIRE_INTERNAL_AUTH** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa REQUIRE_INTERNAL_AUTH.
- Prod: sau khi sửa REQUIRE_INTERNAL_AUTH, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback REQUIRE_INTERNAL_AUTH: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**INTERNAL_SERVICE_TOKEN** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa INTERNAL_SERVICE_TOKEN.
- Prod: sau khi sửa INTERNAL_SERVICE_TOKEN, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback INTERNAL_SERVICE_TOKEN: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

---

### §J.1.67 — Nhóm `SSO`: tương tác chéo

Các biến: `OAUTH_PROVIDER`, `OAUTH_CLIENT_ID`, `OAUTH_CLIENT_SECRET`, `OAUTH_REDIRECT_URI`, `AZURE_TENANT_ID`.

**OAUTH_PROVIDER** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa OAUTH_PROVIDER.
- Prod: sau khi sửa OAUTH_PROVIDER, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback OAUTH_PROVIDER: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**OAUTH_CLIENT_ID** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa OAUTH_CLIENT_ID.
- Prod: sau khi sửa OAUTH_CLIENT_ID, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback OAUTH_CLIENT_ID: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**OAUTH_CLIENT_SECRET** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa OAUTH_CLIENT_SECRET.
- Prod: sau khi sửa OAUTH_CLIENT_SECRET, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback OAUTH_CLIENT_SECRET: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**OAUTH_REDIRECT_URI** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa OAUTH_REDIRECT_URI.
- Prod: sau khi sửa OAUTH_REDIRECT_URI, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback OAUTH_REDIRECT_URI: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**AZURE_TENANT_ID** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa AZURE_TENANT_ID.
- Prod: sau khi sửa AZURE_TENANT_ID, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback AZURE_TENANT_ID: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

---

### §J.1.68 — Nhóm `Hardening`: tương tác chéo

Các biến: `REDIS_PASSWORD`, `MONGO_ROOT_USER`, `MONGO_ROOT_PASSWORD`, `PUBLIC_DOMAIN`, `TLS_EMAIL`.

**REDIS_PASSWORD** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa REDIS_PASSWORD.
- Prod: sau khi sửa REDIS_PASSWORD, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback REDIS_PASSWORD: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**MONGO_ROOT_USER** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa MONGO_ROOT_USER.
- Prod: sau khi sửa MONGO_ROOT_USER, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback MONGO_ROOT_USER: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**MONGO_ROOT_PASSWORD** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa MONGO_ROOT_PASSWORD.
- Prod: sau khi sửa MONGO_ROOT_PASSWORD, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback MONGO_ROOT_PASSWORD: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**PUBLIC_DOMAIN** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa PUBLIC_DOMAIN.
- Prod: sau khi sửa PUBLIC_DOMAIN, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback PUBLIC_DOMAIN: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

**TLS_EMAIL** — khi thay đổi biến này, cân nhắc restart các service phụ thuộc và chạy lại smoke test /health/ready.
- Dev: xác minh bằng `curl localhost:18300/health/ready` sau khi sửa TLS_EMAIL.
- Prod: sau khi sửa TLS_EMAIL, recreate container liên quan; kiểm tra log không lộ giá trị secret.
- Rollback TLS_EMAIL: giữ bản backup .env trước deploy; thời gian propagate tối đa 1 chu kỳ restart.

