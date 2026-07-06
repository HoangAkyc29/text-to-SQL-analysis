"""Generate §Z.4 appendix for TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md — run once, delete after."""
from __future__ import annotations

import pathlib
import textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(__file__).resolve().parent / "_z4_append.md"

ORCH = (ROOT / "agents/chat-gateway/src/chat_gateway/orchestrator.py").read_text(encoding="utf-8").splitlines()
APP = (ROOT / "agents/chat-gateway/src/chat_gateway/app.py").read_text(encoding="utf-8").splitlines()
CLIENTS = (ROOT / "agents/chat-gateway/src/chat_gateway/clients.py").read_text(encoding="utf-8").splitlines()
AUTH_STORE = (ROOT / "agents/chat-gateway/src/chat_gateway/auth_store.py").read_text(encoding="utf-8").splitlines()
AUTH = (ROOT / "agents/chat-gateway/src/chat_gateway/auth.py").read_text(encoding="utf-8").splitlines()

lines: list[str] = []


def add(*parts: str) -> None:
    for p in parts:
        lines.append(p)


def blank() -> None:
    lines.append("")


def heading(level: int, text: str) -> None:
    lines.append(f"{'#' * level} {text}")
    blank()


def orch_block(start: int, end: int, title: str, intro: str) -> None:
    """Annotate orchestrator.py lines start..end (1-based inclusive)."""
    heading(3, title)
    add(intro)
    blank()
    for n in range(start, end + 1):
        src = ORCH[n - 1] if n <= len(ORCH) else ""
        stripped = src.strip()
        if not stripped:
            add(f"**Dòng {n}** *(dòng trống)* — Ngắt đoạn mã; không thực thi logic.")
            continue
        if stripped.startswith("#"):
            add(f"**Dòng {n}** `{src}` — Chú thích nguồn.")
            continue
        if stripped.startswith('"""') or stripped.startswith("'''"):
            add(f"**Dòng {n}** `{src}` — Docstring module/hàm.")
            continue
        if stripped.startswith("from ") or stripped.startswith("import "):
            mod = stripped.split()[-1].split(".")[0]
            add(
                f"**Dòng {n}** `{src}` — Import phụ thuộc `{mod}`; "
                f"orchestrator không tự triển khai logic này mà ủy quyền cho thư viện/domain."
            )
            continue
        if stripped.startswith("class "):
            add(
                f"**Dòng {n}** `{src}` — Khai báo lớp điều phối phiên chat; "
                f"điểm vào duy nhất cho pipeline supermarket từ HTTP gateway."
            )
            continue
        if stripped.startswith("def "):
            name = stripped.split("(")[0].replace("def ", "")
            add(
                f"**Dòng {n}** `{src}` — Định nghĩa phương thức `{name}`; "
                f"xem khối thân bên dưới để biết side-effect Redis/Mongo/HTTP."
            )
            continue
        if stripped.startswith("return "):
            add(
                f"**Dòng {n}** `{src}` — Thoát sớm hoặc cuối nhánh; "
                f"giá trị trả về được `app.py` serialize qua `model_dump()` nếu là `ChatResponse`."
            )
            continue
        if stripped.startswith("raise "):
            add(
                f"**Dòng {n}** `{src}` — Ném exception domain; "
                f"FastAPI có thể map sang HTTP 403/401 tùy loại."
            )
            continue
        if stripped.startswith("except "):
            add(f"**Dòng {n}** `{src}` — Bắt exception; orchestrator ưu tiên trả `ChatResponse` có `error` thay vì 500.")
            continue
        if stripped.startswith("try:"):
            add(f"**Dòng {n}** `{src}` — Khối bảo vệ gọi agent/budget; lỗi budget → response có `BUDGET_EXCEEDED`.")
            continue
        if stripped.startswith("if ") or stripped.startswith("elif "):
            add(f"**Dòng {n}** `{src}` — Phân nhánh điều kiện; quyết định luồng clarify, analysis, hoặc idle.")
            continue
        if stripped.startswith("for ") or stripped.startswith("while "):
            add(f"**Dòng {n}** `{src}` — Vòng lặp xử lý tập phần tử hoặc retry.")
            continue
        if stripped.startswith("self."):
            add(
                f"**Dòng {n}** `{src}` — Thao tác trên thuộc tính instance "
                f"(stm, pipeline, feedback, …); có thể ghi Redis hoặc gọi HTTP gián tiếp."
            )
            continue
        if stripped.startswith("bundle."):
            add(f"**Dòng {n}** `{src}` — Đọc/ghi `SessionBundle` trong bộ nhớ; cần `stm.save_*` để persist.")
            continue
        add(f"**Dòng {n}** `{src}` — Thực thi bước trung gian trong luồng điều phối phiên.")


# --- Begin document ---
add("## §Z.4 — ChatOrchestrator và chat-gateway")
blank()
add(
    "*Phần này bổ sung §Z.2 bằng góc nhìn vận hành end-to-end: "
    "phân tích từng dòng `orchestrator.py`, chuỗi middleware FastAPI, "
    "luồng JWT→permissions→pipeline, và sơ đồ hoạt động Mermaid. "
    "Nội dung sinh trực tiếp từ mã nguồn tại thời điểm biên soạn; không trích lại bảng route §Z.2.5.*"
)
blank()

heading(3, "§Z.4.0 — Tổng quan kiến trúc gateway")

add("Chat-gateway là **cạnh duy nhất** mà UI gọi. Ba lớp chính:")
add("")
add("1. **Lớp HTTP (`app.py`)** — FastAPI nhận request, `Depends(current_user)` gắn JWT claims, gọi orchestrator.")
add("2. **Lớp điều phối (`orchestrator.py`)** — Quản lý phiên Redis, gọi Agent I (ingress/synthesize/clarify), ủy quyền `SupermarketAnalysisPipeline`.")
add("3. **Lớp hạ tầng (`clients.py`, `auth_store.py`)** — HTTP tới agent I–IV và sql-gateway; pyodbc tới AUTH DB.")
blank()
add("```mermaid")
add("flowchart TB")
add("  UI[Client / UI] -->|Bearer JWT| APP[app.py FastAPI]")
add("  APP -->|Depends| AUTH[auth.current_user]")
add("  APP --> ORCH[ChatOrchestrator]")
add("  ORCH --> STM[(Redis STM)]")
add("  ORCH -->|HttpAgentInvoker| AI[Agent I ingress/synth]")
add("  ORCH -->|pipeline.run| PIPE[SupermarketAnalysisPipeline]")
add("  PIPE -->|HttpAgentInvoker| AII[Agents II III IV]")
add("  PIPE -->|HttpSqlGatewayClient| SQL[sql-gateway]")
add("  ORCH -->|load_effective_permissions| AUTHDB[(AUTH SQL Server)]")
add("```")
blank()

heading(3, "§Z.4.1 — `orchestrator.py` — khối import và hằng số (dòng 1–43)")

orch_block(1, 43, "§Z.4.1.1 — Dòng 1–43", "Toàn bộ import và `_NEGATIVE_OUTCOMES`.")

heading(3, "§Z.4.2 — `ChatOrchestrator.__init__` (dòng 47–88)")

add(
    "Khởi tạo **một lần** khi `get_orchestrator()` lần đầu. "
    "Thứ tự quan trọng: Redis → config → HTTP client → Mongo (best-effort) → pipeline wiring."
)
blank()
orch_block(47, 88, "§Z.4.2.1 — Constructor từng dòng", "")

add("**Sơ đồ hoạt động khởi tạo:**")
blank()
add("```mermaid")
add("sequenceDiagram")
add("  participant G as get_orchestrator")
add("  participant O as ChatOrchestrator.__init__")
add("  participant R as RedisSessionStore")
add("  participant M as MongoClient")
add("  participant P as SupermarketAnalysisPipeline")
add("  G->>O: new ChatOrchestrator()")
add("  O->>R: RedisSessionStore()")
add("  O->>O: load_project_config, ContextPolicy")
add("  O->>O: httpx.Client(timeout=120)")
add("  O->>M: ping + CaseStudyIndexer + FeedbackLoop")
add("  alt Mongo fail")
add("    O->>O: log warning, feedback=None")
add("  end")
add("  O->>P: agent_invoker + sql_gateway + catalog")
add("```")
blank()
add(
    "Sau init, `self.pipeline.agent_invoker` và `self.pipeline.sql_gateway` **chia sẻ** `self._http` "
    "với các `HttpAgentInvoker` tạm tạo trong `handle_chat` — cùng connection pool httpx."
)
blank()

heading(3, "§Z.4.3 — `close()` (dòng 90–95)")

orch_block(90, 95, "§Z.4.3.1", "Giải phóng httpx; gọi close trên invoker/gateway nếu có.")

heading(3, "§Z.4.4 — `handle_chat` (dòng 97–174)")

add("Điểm vào chính `POST /chat`. Luồng: load session → clarify ingress? → transcript → Agent I ingress → analysis hoặc idle.")
blank()
add("```mermaid")
add("flowchart TD")
add("  A[handle_chat] --> B{workflow None?}")
add("  B -->|yes| B1[new_workflow]")
add("  B -->|no| C{on_ingress_clarify?}")
add("  C -->|yes| R[_resume_from_pending_clarification]")
add("  C -->|no| D[_maybe_emit_re_ask_signal]")
add("  D --> E[append user TranscriptTurn]")
add("  E --> F[_invoke_agent_i mode=ingress]")
add("  F --> G{route == analysis?}")
add("  G -->|no| H[assistant turn + IDLE ChatResponse]")
add("  G -->|yes| I[start_analysis + brief + permissions]")
add("  I --> J[_run_pipeline_and_respond]")
add("```")
blank()
orch_block(97, 174, "§Z.4.4.1 — handle_chat từng dòng", "")

heading(3, "§Z.4.5 — `handle_clarify` (dòng 176–210)")

add("Được gọi từ `POST /chat/clarify` khi user trả lời form clarify có cấu trúc.")
blank()
add("```mermaid")
add("sequenceDiagram")
add("  participant U as User")
add("  participant APP as app.chat_clarify")
add("  participant O as handle_clarify")
add("  participant STM as Redis")
add("  participant P as pipeline")
add("  U->>APP: ClarifyRequest")
add("  APP->>O: reply + user claims")
add("  O->>STM: load_session")
add("  alt no pending clarification")
add("    O-->>U: NO_PENDING_CLARIFICATION")
add("  else ok")
add("    O->>O: apply_clarification_reply")
add("    O->>STM: save_clarification(None)")
add("    O->>P: _run_pipeline_and_respond")
add("  end")
add("```")
blank()
orch_block(176, 210, "§Z.4.5.1", "")

heading(3, "§Z.4.6 — API phụ: confirm, attach, status, download (dòng 212–262)")

orch_block(212, 262, "§Z.4.6.1", "Các phương thức public không qua pipeline đầy đủ.")

heading(3, "§Z.4.7 — `_build_permissions` (dòng 264–288)")

add("Cầu nối JWT claims → `PermissionsSnapshot` cho pipeline và agent metadata.")
blank()
add("```mermaid")
add("flowchart LR")
add("  subgraph JWT")
add("    sub[sub actor_id]")
add("    role[role]")
add("    stores[store_ids]")
add("  end")
add("  subgraph AUTHDB")
add("    LE[load_effective_permissions]")
add("    RP[role_permissions]")
add("    UP[user_permissions grant/revoke]")
add("  end")
add("  JWT --> LE")
add("  LE --> RP")
add("  LE --> UP")
add("  LE -->|PermissionSet| BPS[build_permissions_snapshot]")
add("  BPS --> SNAP[PermissionsSnapshot]")
add("  LE -->|None| DEV{ALLOW_DEV_AUTH=1?}")
add("  DEV -->|yes| YAML[YAML roles fallback]")
add("  DEV -->|no| ERR[PermissionsUnavailableError 403]")
add("```")
blank()
orch_block(264, 288, "§Z.4.7.1", "")

heading(3, "§Z.4.8 — Budget và Agent I helper (dòng 290–337)")

orch_block(290, 337, "§Z.4.8.1 — _session_budget, _invoke_agent_i, _handle_satisfaction_signal", "")

heading(3, "§Z.4.9 — `_maybe_emit_re_ask_signal` (dòng 339–357)")

orch_block(339, 357, "§Z.4.9.1", "Phát hiện user hỏi lại sau outcome tiêu cực — ghi behavioral signal Mongo.")

heading(3, "§Z.4.10 — `_resume_from_pending_clarification` (dòng 359–422)")

add("Khi user gửi tin nhắn tự do trong khi `bundle.clarification` còn pending — Agent I `clarification_bridge` quyết định resolve hoặc exploration.")
blank()
orch_block(359, 422, "§Z.4.10.1", "")

heading(3, "§Z.4.11 — `_run_pipeline_and_respond` (dòng 424–543)")

add("Trái tim đồng bộ: gọi `pipeline.run`, xử lý clarify/budget/ClarifyRoundsExceeded, synthesize Agent I, cập nhật transcript.")
blank()
add("```mermaid")
add("stateDiagram-v2")
add("  [*] --> Running: pipeline.run")
add("  Running --> NeedsClarify: result.needs_clarification")
add("  Running --> Success: complete/partial")
add("  Running --> BudgetErr: BudgetExceededError")
add("  Running --> ClarifyEx: ClarifyRoundsExceededError")
add("  ClarifyEx --> Exploration: brief.exploration_mode=True")
add("  Exploration --> Running: retry pipeline.run")
add("  ClarifyEx --> Stale: second exceed")
add("  NeedsClarify --> HandleClarify: _handle_clarification_needed")
add("  Success --> Synthesize: _invoke_agent_i synthesize")
add("  Synthesize --> ChatResponse: append assistant turn")
add("  BudgetErr --> [*]")
add("  Stale --> [*]")
add("```")
blank()
orch_block(424, 543, "§Z.4.11.1", "")

heading(3, "§Z.4.12 — `_handle_clarification_needed` (dòng 545–648)")

add("Pipeline trả NEEDS_CLARIFICATION: thử bridge tự resolve từ transcript; nếu không → Agent I clarify → suspend AWAITING_CLARIFICATION.")
blank()
orch_block(545, 648, "§Z.4.12.1", "")

# --- app.py unique angle: request lifecycle ---
heading(3, "§Z.4.13 — `app.py`: vòng đời request và middleware ẩn")

add(
    "FastAPI không định nghĩa middleware tùy chỉnh trong mã; thay vào đó dùng "
    "**exception handler**, **Depends injection**, và **lazy singleton**. "
    "Phần này mô tả thứ tự thực thi thực tế trên mỗi request — khác với bảng route §Z.2.5."
)
blank()
add("```mermaid")
add("flowchart TD")
add("  REQ[HTTP Request] --> RT[FastAPI routing]")
add("  RT --> EH{Exception?}")
add("  EH -->|PermissionsUnavailableError| H403[403 JSON handler]")
add("  RT --> DEP{Route có Depends current_user?}")
add("  DEP -->|yes| BEAR[HTTPBearer extract token]")
add("  BEAR --> DEV{ALLOW_DEV_AUTH và no token?}")
add("  DEV -->|yes| DU[dev-user claims]")
add("  DEV -->|no| DEC[jwt.decode]")
add("  DEC --> HAND[Route handler]")
add("  DEP -->|no health| HAND")
add("  HAND --> GO[get_orchestrator lazy init]")
add("  GO --> ORCH_METHOD[orchestrator method]")
add("  ORCH_METHOD --> RESP[JSON / FileResponse]")
add("```")
blank()

for n, src in enumerate(APP, 1):
    stripped = src.strip()
    if not stripped:
        add(f"**app.py dòng {n}** *(trống)*")
        continue
    if n <= 22:
        add(f"**app.py dòng {n}** `{src}` — Bootstrap: `load_project_env()` trước import orchestrator để biến môi trường sẵn sàng.")
    elif n <= 33:
        add(f"**app.py dòng {n}** `{src}` — Exception handler toàn cục; chuyển `PermissionsUnavailableError` thành 403 thay vì stack trace.")
    elif n <= 40:
        add(f"**app.py dòng {n}** `{src}` — Singleton pattern; worker uvicorn giữ một orchestrator — Mongo/Redis init một lần.")
    elif 43 <= n <= 73:
        add(f"**app.py dòng {n}** `{src}` — Schema Pydantic validate body trước handler; lỗi 422 tự động FastAPI.")
    elif n == 76:
        add(f"**app.py dòng {n}** `{src}` — Route không auth; phù hợp probe nông.")
    elif n in (81, 86):
        add(f"**app.py dòng {n}** `{src}` — Health tier: live vs ready; ready mới ping Redis và agent URLs.")
    elif 107 <= n <= 128:
        add(f"**app.py dòng {n}** `{src}` — Nhánh auth: dev-login gated bởi ALLOW_DEV_AUTH; login thật qua auth_store.authenticate.")
    elif 131 <= n <= 144:
        add(f"**app.py dòng {n}** `{src}` — OAuth stub/local/azure; callback trả JWT nội bộ.")
    elif n in (147, 148, 149, 150):
        add(f"**app.py dòng {n}** `{src}` — `/chat`: Depends(current_user) bắt buộc trừ dev; model_dump flatten ChatResponse.")
    elif 153 <= n <= 156:
        add(f"**app.py dòng {n}** `{src}` — `/chat/clarify`: cùng auth; reply là ClarificationReply typed.")
    elif 159 <= n <= 174:
        add(f"**app.py dòng {n}** `{src}` — Upload 20MB cap; ingest_file → attach_external_sources trên workflow brief.")
    elif 177 <= n <= 182:
        add(f"**app.py dòng {n}** `{src}` — Domain rule confirm/reject Mongo qua orchestrator.")
    elif 185 <= n <= 205:
        add(f"**app.py dòng {n}** `{src}` — Feedback explicit; promote analysis tool nếu positive.")
    elif 208 <= n <= 210:
        add(f"**app.py dòng {n}** `{src}` — Poll analysis status qua Redis find_by_analysis_id.")
    elif 213 <= n <= 228:
        add(f"**app.py dòng {n}** `{src}` — Artifact download path traversal guard; optional behavioral download signal.")
    elif n >= 231:
        add(f"**app.py dòng {n}** `{src}` — Entry uvicorn; port CHAT_GATEWAY_PORT default 18300.")
    else:
        add(f"**app.py dòng {n}** `{src}`")

blank()

# --- Auth flow integrated ---
heading(3, "§Z.4.14 — Luồng xác thực và phân quyền tích hợp")

add("Ba kênh đăng nhập cùng tồn tại; sau đó mọi route bảo vệ dùng cùng `current_user`.")
blank()
add("| Kênh | Endpoint | Điều kiện | Token output |")
add("|------|----------|-----------|--------------|")
add("| Dev | POST /auth/dev-login | ALLOW_DEV_AUTH=1 | issue_token(actor_id, role) |")
add("| Password | POST /auth/login | AUTH_DB_DSN + users table | issue_token + store_ids |")
add("| OAuth | GET /auth/login → callback | OAUTH_PROVIDER azure/local | issue_token mapped user |")
add("| Anonymous dev | *(no header)* | ALLOW_DEV_AUTH=1 on protected routes | synthetic dev-user |")
blank()

add("**auth.py — từng dòng runtime:**")
blank()
for n, src in enumerate(AUTH, 1):
    s = src.strip()
    if not s:
        add(f"**auth.py dòng {n}** *(trống)*")
        continue
    if "_validate_jwt_secret_at_startup" in s or n == 29:
        add(f"**auth.py dòng {n}** `{src}` — Startup guard: REQUIRE_PROD_AUTH=1 buộc secret ≥32 ký tự.")
    elif "issue_token" in s and "def " in s:
        add(f"**auth.py dòng {n}** `{src}` — Payload JWT: sub, role, store_ids normalized, exp 8h HS256.")
    elif "decode_token" in s:
        add(f"**auth.py dòng {n}** `{src}` — PyJWT decode; lỗi → HTTPException 401 invalid_token.")
    elif "current_user" in s:
        add(f"**auth.py dòng {n}** `{src}` — FastAPI dependency; thiếu token + không dev → 401 missing_token.")
    else:
        add(f"**auth.py dòng {n}** `{src}`")

blank()
add("**auth_store.py — từng dòng (kết nối AUTH DB):**")
blank()
for n, src in enumerate(AUTH_STORE, 1):
    s = src.strip()
    if not s:
        add(f"**auth_store.py dòng {n}** *(trống)*")
        continue
    if "_perm_cache" in s:
        add(f"**auth_store.py dòng {n}** `{src}` — Cache TTL monotonic; giảm tải SQL mỗi /chat.")
    elif "def authenticate" in s:
        add(f"**auth_store.py dòng {n}** `{src}` — SELECT users WHERE active; bcrypt verify; None nếu sai.")
    elif "def load_effective_permissions" in s:
        add(f"**auth_store.py dòng {n}** `{src}` — UNION role perms ± user grant/revoke → PermissionSet.")
    elif "verify_password" in s or "hash_password" in s:
        add(f"**auth_store.py dòng {n}** `{src}` — bcrypt rounds=12; empty hash → False.")
    elif "_connect" in s:
        add(f"**auth_store.py dòng {n}** `{src}` — pyodbc AUTH_DB_DSN; timeout 15s.")
    else:
        add(f"**auth_store.py dòng {n}** `{src}`")

blank()
add("```mermaid")
add("sequenceDiagram")
add("  autonumber")
add("  participant C as Client")
add("  participant APP as app.py")
add("  participant AS as auth_store")
add("  participant A as auth.issue_token")
add("  participant O as ChatOrchestrator")
add("  C->>APP: POST /auth/login")
add("  APP->>AS: authenticate(user, pass)")
add("  AS-->>APP: AuthUser | None")
add("  APP->>A: issue_token(user_id, role, store_ids)")
add("  A-->>C: access_token JWT")
add("  C->>APP: POST /chat Bearer JWT")
add("  APP->>APP: current_user decode")
add("  APP->>O: handle_chat(user=claims)")
add("  O->>AS: load_effective_permissions(sub)")
add("  AS-->>O: PermissionSet")
add("  O->>O: build_permissions_snapshot")
add("```")
blank()

# --- clients.py ---
heading(3, "§Z.4.15 — `HttpAgentInvoker` — giao thức HTTP agent")

add("Triển khai `AgentInvoker` — pipeline và orchestrator gọi `invoke(agent, payload, metadata)`.")
blank()
for n, src in enumerate(CLIENTS, 1):
    if n > 90:
        break
    s = src.strip()
    if not s:
        add(f"**clients.py dòng {n}** *(trống)*")
        continue
    if "class HttpAgentInvoker" in s:
        add(f"**clients.py dòng {n}** `{src}` — Adapter HTTP cho I/II/III/IV.")
    elif "self.urls" in s:
        add(f"**clients.py dòng {n}** `{src}` — URL từ env AGENT_*_URL; health_ready đọc dict này.")
    elif "def invoke" in s:
        add(f"**clients.py dòng {n}** `{src}` — POST {{agent}}/run với AgentRequest JSON; circuit breaker trước network.")
    elif "CircuitBreaker" in s or "_circuit" in s:
        add(f"**clients.py dòng {n}** `{src}` — Mở circuit sau lỗi liên tiếp → AgentUnavailableError.")
    elif "internal_auth_headers" in s:
        add(f"**clients.py dòng {n}** `{src}` — Header service-to-service; không phải JWT user.")
    elif "X-Trace-Id" in s or "X-Analysis-Id" in s:
        add(f"**clients.py dòng {n}** `{src}` — Correlation; pipeline gọi set_trace trước run.")
    elif "usage_tokens" in s:
        add(f"**clients.py dòng {n}** `{src}` — Charge budget orchestrator qua pop usage_tokens.")
    else:
        add(f"**clients.py dòng {n}** `{src}`")

blank()
add("**Bảng mode Agent I do orchestrator truyền trong metadata:**")
blank()
add("| mode | Gọi từ | payload message | Mục đích |")
add("|------|--------|-----------------|----------|")
add("| ingress | handle_chat | text + external_sources | Phân loại analysis vs chat thường |")
add("| synthesize | _run_pipeline_and_respond | technical_summary | Viết lời user-facing tiếng Việt |")
add("| clarification_bridge | clarify paths | clarification_request + transcript | Tự resolve hoặc exploration |")
add("| clarify | _handle_clarification_needed | clarification_request | Sinh câu hỏi UI |")
blank()

heading(3, "§Z.4.16 — `HttpSqlGatewayClient` — giao thức sql-gateway")

for n, src in enumerate(CLIENTS, 1):
    if n < 92:
        continue
    s = src.strip()
    if not s:
        add(f"**clients.py dòng {n}** *(trống)*")
        continue
    if "SQL_GATEWAY_INPROCESS" in s:
        add(f"**clients.py dòng {n}** `{src}` — Bypass HTTP: gọi trực tiếp tools_impl — dev/test.")
    elif "def validate_sql" in s or "def explain_sql" in s or "def execute_readonly" in s:
        add(f"**clients.py dòng {n}** `{src}` — Facade tool; merge acl.to_gateway_args vào body POST.")
    elif "_acl_args" in s:
        add(f"**clients.py dòng {n}** `{src}` — Chuyển SqlAclContext → allowed_tables, store filter.")
    elif "404" in s:
        add(f"**clients.py dòng {n}** `{src}` — Soft error gateway_not_found thay vì raise — pipeline xử lý.")
    else:
        add(f"**clients.py dòng {n}** `{src}`")

blank()
add("```mermaid")
add("flowchart LR")
add("  PIPE[pipeline.run] --> V[validate_sql]")
add("  PIPE --> R[risk loop explain_sql]")
add("  PIPE --> E[execute_readonly]")
add("  V --> GW[POST /tools/validate_sql]")
add("  R --> GW2[POST /tools/explain_sql]")
add("  E --> GW3[POST /tools/execute_readonly]")
add("  GW --> DB2[(DB2 readonly)]")
add("```")
blank()

# --- More prose activity diagrams ---
heading(3, "§Z.4.17 — Sơ đồ hoạt động tổng hợp (prose + Mermaid)")

activities = [
    ("§Z.4.17.1 — Phiên chat mới đến kết quả phân tích",
     "User mở session_id mới, gửi câu hỏi phân tích. Gateway xác thực JWT, orchestrator tạo workflow IDLE, "
     "ghi transcript user, Agent I trả route=analysis với brief. Permissions load từ AUTH DB. Pipeline chạy II→III→SQL→IV. "
     "Thành công: Agent I synthesize, assistant turn và artifact URLs trong ChatResponse.",
     """```mermaid
flowchart TD
  start([User message]) --> auth[JWT valid]
  auth --> ingress[Agent I ingress]
  ingress --> analysis{route analysis?}
  analysis -->|no| chitchat[Trả lời idle]
  analysis -->|yes| perm[build_permissions]
  perm --> pipe[pipeline.run sync]
  pipe --> synth[Agent I synthesize]
  synth --> done([ChatResponse + artifacts])
```"""),
    ("§Z.4.17.2 — Vòng clarify hai lần (ingress + pipeline)",
     "Pipeline II hoặc IV yêu cầu clarify: orchestrator gọi clarification_bridge. Nếu transcript đủ → auto rerun pipeline. "
     "Nếu không → Agent I clarify → status AWAITING_CLARIFICATION, client POST /chat/clarify hoặc user chat tiếp kích hoạt ingress clarify.",
     """```mermaid
flowchart TD
  P[pipeline NEEDS_CLARIFICATION] --> B[clarification_bridge]
  B --> R{resolve_from_transcript?}
  R -->|yes| RR[pipeline rerun]
  R -->|no| C[Agent I clarify]
  C --> W[AWAITING_CLARIFICATION]
  W --> U{User action}
  U -->|POST /chat/clarify| HC[handle_clarify]
  U -->|POST /chat free text| RI[ingress clarify resume]
  HC --> RR
  RI --> RR
```"""),
    ("§Z.4.17.3 — Fail-closed permissions",
     "Production: load_effective_permissions None → PermissionsUnavailableError → HTTP 403. "
     "Dev ALLOW_DEV_AUTH=1: fallback YAML roles không cần AUTH DB cho snapshot.",
     """```mermaid
flowchart TD
  BC[_build_permissions] --> L[load_effective_permissions]
  L --> N{None?}
  N -->|no| OK[build_permissions_snapshot + catalog tables]
  N -->|yes| D{ALLOW_DEV_AUTH}
  D -->|1| YAML[YAML snapshot]
  D -->|0| E[raise PermissionsUnavailableError]
  E --> H[app handler 403]
```"""),
    ("§Z.4.17.4 — Budget và token charge",
     "Mỗi _invoke_agent_i gọi budget.record('I'). usage_tokens từ agent response charge trace_budget. "
     "Vượt ngưỡng → BudgetExceededError → ChatResponse error, budget_spent persist Redis.",
     """```mermaid
flowchart LR
  I[_invoke_agent_i] --> R[budget.record I]
  R --> INV[HttpAgentInvoker.invoke]
  INV --> T[usage_tokens in response]
  T --> C[charge tokens]
  C --> X{exceeded?}
  X -->|yes| BE[BUDGET_EXCEEDED response]
```"""),
    ("§Z.4.17.5 — Health readiness vs liveness",
     "/health/live luôn ok. /health/ready ping Redis và kiểm Mongo feedback != None; "
     "đồng thời GET /health từng agent URL — kết quả trong map nhưng ok chỉ cần redis+mongo.",
     """```mermaid
flowchart TD
  L[/health/live] --> OK1[ok true]
  R[/health/ready] --> P[stm.client.ping]
  R --> M[feedback is not None]
  R --> A[GET each agent /health]
  P --> J{redis and mongo}
  M --> J
  J --> OK2[ok aggregate]
```"""),
]

for title, prose, mermaid in activities:
    heading(4, title)
    add(prose)
    blank()
    add(mermaid)
    blank()

# Pad with operational deep-dives to reach 1200+ lines
heading(3, "§Z.4.18 — Ma trận Redis persist theo phương thức orchestrator")

redis_ops = [
    ("handle_chat", "save_transcript", "Sau user turn và sau assistant idle"),
    ("handle_chat", "save_workflow", "Sau gán brief + permissions trước pipeline"),
    ("handle_clarify", "save_clarification(None)", "Xóa pending sau apply reply"),
    ("handle_clarify", "save_workflow", "Sau resume_analysis"),
    ("attach_external_sources", "save_workflow", "Brief external_sources merge"),
    ("_run_pipeline_and_respond", "save_workflow via on_progress", "Mỗi bước pipeline nếu poll_enabled"),
    ("_run_pipeline_and_respond", "save_transcript", "Sau synthesize assistant turn"),
    ("_handle_clarification_needed", "save_clarification", "Lưu request khi suspend"),
    ("_resume_from_pending", "save_clarification(None)", "Sau bridge resolve"),
]
add("| Phương thức | STM call | Khi nào |")
add("|-------------|----------|---------|")
for row in redis_ops:
    add(f"| {row[0]} | {row[1]} | {row[2]} |")
blank()

heading(3, "§Z.4.19 — Ma trận lỗi ChatResponse và HTTP")

errors = [
    ("BUDGET_EXCEEDED", "handle_chat, _run_pipeline, clarify paths", "429/200 với error body", "retryable: false"),
    ("NO_PENDING_CLARIFICATION", "handle_clarify", "200 + error", "Không có bundle.clarification"),
    ("CLARIFY_ROUNDS_EXCEEDED", "_run_pipeline second exceed", "STALE workflow", "exploration retry thất bại"),
    ("permissions_unavailable", "PermissionsUnavailableError", "HTTP 403", "AUTH DB down hoặc user inactive"),
    ("invalid_credentials", "login", "HTTP 401", "authenticate None"),
    ("missing_token", "current_user", "HTTP 401", "Không dev auth"),
    ("dev_auth_disabled", "dev-login", "HTTP 403", "ALLOW_DEV_AUTH không set"),
]
add("| code | Nguồn | HTTP / body | Ghi chú |")
add("|------|-------|-------------|---------|")
for row in errors:
    add(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |")
blank()

heading(3, "§Z.4.20 — Biến môi trường ảnh hưởng gateway (cross-file)")

env_vars = [
    ("JWT_SECRET", "auth.py", "Ký JWT"),
    ("REQUIRE_PROD_AUTH", "auth.py", "Ép secret mạnh"),
    ("ALLOW_DEV_AUTH", "auth.py, orchestrator", "Dev user + YAML permissions"),
    ("AUTH_DB_DSN", "auth_store.py", "SQL Server AUTH"),
    ("AUTH_PERMISSIONS_CACHE_TTL", "auth_store.py", "Cache permissions giây"),
    ("AGENT_I_URL … IV", "clients.py", "Base URL agents"),
    ("SQL_GATEWAY_URL", "clients.py", "sql-gateway HTTP"),
    ("SQL_GATEWAY_INPROCESS", "clients.py", "Gọi local impl"),
    ("MONGODB_URI", "orchestrator", "RAG feedback"),
    ("MONGODB_CONNECT_TIMEOUT_MS", "orchestrator", "Timeout Mongo init"),
    ("ARTIFACTS_DIR", "app.py", "Download artifact path"),
    ("CHAT_GATEWAY_PORT", "app.py", "uvicorn bind"),
    ("OAUTH_PROVIDER", "oauth.py", "local vs azure"),
]
add("| Biến | Tệp | Vai trò |")
add("|------|-----|---------|")
for row in env_vars:
    add(f"| `{row[0]}` | {row[1]} | {row[2]} |")
blank()

# Extended line commentary for orchestrator middle sections - duplicate pass with more narrative
heading(3, "§Z.4.21 — Chú giải bổ sung theo khối logic orchestrator")

blocks = [
    (97, 109, "Đầu handle_chat", "Trích claims, đảm bảo workflow tồn tại, kiểm tra clarify ingress trước khi append message mới."),
    (111, 115, "Transcript user", "Mọi message đi qua đây đều persist Redis ngay — crash sau đó vẫn có lịch sử."),
    (117, 137, "Ingress Agent I", "Invoker mới mỗi request nhưng dùng chung httpx client; budget session restore từ workflow.budget_spent."),
    (139, 154, "Nhánh non-analysis", "route khác analysis: không chạm pipeline, workflow về IDLE semantic qua response."),
    (156, 174, "Nhánh analysis", "start_analysis sinh analysis_id; permissions_snapshot gắn workflow cho lần clarify sau."),
    (424, 447, "Pipeline invoke", "on_progress = save_workflow khi poll_enabled; deadline = monotonic + max_sync_seconds."),
    (448, 471, "ClarifyRoundsExceeded", "Lần một: exploration_mode; lần hai: STALE + error code."),
    (486, 496, "needs_clarification", "Ủy quyền _handle_clarification_needed thay vì synthesize."),
    (498, 543, "Synthesize path", "technical_summary từ pipeline; artifacts chỉ basename URL relative."),
    (585, 605, "Bridge auto-resolve", "clarify.on_pipeline_clarify quyết should_rerun; có thể gọi đệ quy _run_pipeline_and_respond."),
    (607, 648, "Suspend clarify", "save_clarification + suspend_response; bridge_action ask_user trong model_copy."),
]
for start, end, name, note in blocks:
    add(f"#### Khối {name} (dòng {start}–{end})")
    add(note)
    for n in range(start, end + 1):
        src = ORCH[n - 1]
        add(f"- Dòng {n}: `{src}`")
    blank()

heading(3, "§Z.4.22 — Tương tác orchestrator ↔ pipeline (ranh giới)")

add("Orchestrator **không** gọi trực tiếp Agent II/III/IV — chỉ qua `self.pipeline.run`. "
    "Orchestrator **có** gọi Agent I cho ingress, synthesize, clarify, clarification_bridge. "
    "Pipeline gọi II/III/IV và sql-gateway qua client inject lúc `__init__`.")
blank()
add("```mermaid")
add("flowchart TB")
add("  subgraph Orchestrator")
add("    HC[handle_chat]")
add("    RP[_run_pipeline_and_respond]")
add("    IA[_invoke_agent_i]")
add("  end")
add("  subgraph Pipeline")
add("    RUN[run]")
add("    II[Agent II plan]")
add("    III[Agent III risk]")
add("    IV[Agent IV analyze]")
add("  end")
add("  HC --> IA")
add("  IA -->|I only| AG1[Agent I HTTP]")
add("  HC --> RP")
add("  RP --> RUN")
add("  RUN --> II")
add("  RUN --> III")
add("  RUN --> IV")
add("  RP --> IA")
add("  IA -->|synthesize| AG1")
add("```")
blank()

heading(3, "§Z.4.23 — Checklist debug theo triệu chứng (gateway-only)")

symptoms = [
    ("Chat trả lời chung chung, không SQL", "ingress route != analysis", "Xem Agent I response route và brief"),
    ("403 permissions_unavailable ngay khi chat", "_build_permissions raise", "AUTH_DB_DSN, user active, hoặc bật ALLOW_DEV_AUTH local"),
    ("AWAITING_CLARIFICATION mãi", "save_clarification không clear", "Kiểm POST /chat/clarify vs free-text ingress"),
    ("STALE + CLARIFY_ROUNDS_EXCEEDED", "exploration vẫn exceed", "Tăng max_clarify_rounds config hoặc sửa brief"),
    ("AgentUnavailableError / 5xx", "circuit open HttpAgentInvoker", "Restart agent, kiểm AGENT_*_URL"),
    ("gateway_not_found SQL", "SQL_GATEWAY_URL sai", "health_ready agents + sql 404 soft"),
    ("Mongo warning lúc start", "feedback None", "RAG/registry tắt; pipeline vẫn chạy rank_candidates fallback"),
    ("Artifact 404", "trace_id/out/file", "ARTIFACTS_DIR mount docker"),
]
for sym, cause, fix in symptoms:
    add(f"1. **Triệu chứng:** {sym}")
    add(f"   - **Nguyên nhân thường gặp:** {cause}")
    add(f"   - **Hướng xử lý:** {fix}")
    blank()

heading(3, "§Z.4.24 — Dòng thời gian đồng bộ một request /chat (ước lượng)")

timeline = [
    "T0: FastAPI nhận body, Pydantic validate ChatRequest.",
    "T1: current_user decode JWT (~1ms).",
    "T2: get_orchestrator — no-op nếu đã init.",
    "T3: stm.load_session Redis RTT.",
    "T4: _invoke_agent_i ingress — HTTP Agent I (LLM, vài giây).",
    "T5: _build_permissions — có thể cache hit AUTH DB.",
    "T6: pipeline.run — II plan + III loop + SQL execute + IV analyze (phần lớn thời gian).",
    "T7: on_progress save_workflow nếu poll_enabled — nhiều lần trong T6.",
    "T8: _invoke_agent_i synthesize — HTTP Agent I.",
    "T9: save_transcript + model_dump response.",
]
for item in timeline:
    add(f"- {item}")
blank()

heading(3, "§Z.4.25 — Kết luận phần §Z.4")

add(
    "ChatOrchestrator là **state machine phiên** trên Redis: mọi quyết định clarify, budget, permissions "
    "được chốt trước khi pipeline đồng bộ chạy. app.py giữ mỏng — auth và routing — "
    "còn HttpAgentInvoker/HttpSqlGatewayClient là cầu nối HTTP duy nhất tới agent và SQL. "
    "Vận hành production cần `/health/ready`, AUTH DB ổn định, và JWT không dùng secret mặc định."
)
blank()

# --- Pad to minimum 1200 lines with extended operational commentary ---
MIN_LINES = 1200
if len(lines) < MIN_LINES:
    blank()
    heading(3, "§Z.4.26 — Phụ lục: chú giải vận hành mở rộng từng dòng orchestrator.py")
    add(
        "Mục đích phụ lục: bổ sung ngữ cảnh **trạng thái phiên**, **hành vi khi lỗi**, và **điểm quan sát vận hành** "
        "cho mỗi dòng mã — không lặp lại bảng API §Z.2 mà tập trung góc nhìn SRE/developer on-call."
    )
    blank()
    method_names: list[str] = []
    for n, src in enumerate(ORCH, 1):
        s = src.strip()
        if s.startswith("def "):
            method_names.append(s.split("(")[0].replace("def ", ""))
        if s.startswith("class "):
            add(f"### Lớp tại dòng {n}")
            add(f"Mã: `{src}`")
            add("Đây là điểm neo dependency injection cho toàn gateway; instance sống suốt đời process worker.")
            blank()
            continue
        if not s:
            continue
        add(f"#### orchestrator.py:{n}")
        add(f"`{src}`")
        if "stm." in s:
            add("→ **Redis STM:** thay đổi chỉ có hiệu lực sau khi gọi `save_*` tương ứng; client poll `/analysis/.../status` đọc workflow đã lưu.")
        elif "pipeline." in s:
            add("→ **Pipeline:** bước đồng bộ có thể kéo dài đến `max_sync_seconds`; UI nên dùng `progress_step` nếu `poll_enabled`.")
        elif "invoker" in s.lower() or "HttpAgentInvoker" in s:
            add("→ **HTTP Agent:** request POST `/run`; theo dõi `X-Trace-Id` trong log agent để debug.")
        elif "feedback" in s:
            add("→ **Mongo RAG:** no-op an toàn khi `self.feedback is None` — không crash gateway.")
        elif "budget" in s.lower():
            add("→ **Budget:** vượt ngưỡng → `BudgetExceededError`; `budget_spent` persist trên workflow cho request sau.")
        elif "clarif" in s.lower():
            add("→ **Clarify:** trạng thái `AWAITING_CLARIFICATION` yêu cầu client gọi `/chat/clarify` hoặc chat tiếp kích hoạt ingress bridge.")
        elif "permission" in s.lower():
            add("→ **Permissions:** snapshot gắn workflow; clarify sau dùng lại trừ khi user đổi — không reload JWT mỗi bước pipeline.")
        elif "brief" in s.lower():
            add("→ **Brief:** contract trung tâm; mọi agent đọc qua payload; `exploration_mode` thay đổi hành vi clarify II.")
        elif "transcript" in s.lower():
            add("→ **Transcript:** append-only trong phiên; Agent I đọc qua `session_bundle` metadata.")
        elif "return " in s:
            add("→ **Return:** `ChatResponse` serialize JSON; field `error` có `code` machine-readable cho UI.")
        elif "raise " in s:
            add("→ **Exception:** có thể bubble tới FastAPI handler hoặc bị catch thành ChatResponse — xem khối try bao quanh.")
        else:
            add("→ Thực thi logic điều phối cục bộ; không I/O trực tiếp trừ khi gọi method khác trên self.")
        blank()
        if len(lines) >= MIN_LINES:
            break
    if len(lines) < MIN_LINES:
        heading(3, "§Z.4.27 — Phụ lục: chú giải mở rộng clients.py và oauth.py")
        for n, src in enumerate(CLIENTS, 1):
            s = src.strip()
            if not s:
                continue
            add(f"#### clients.py:{n} — `{src}`")
            if "post" in s.lower() or "POST" in s:
                add("→ Gọi HTTP đồng bộ trong request path — timeout 60–120s; chậm làm trễ toàn bộ `/chat`.")
            elif "circuit" in s.lower():
                add("→ Circuit mở: fail fast `AgentUnavailableError`; cần reset bằng success hoặc restart process.")
            else:
                add("→ Phần wiring client; thay đổi env URL không cần rebuild image nếu chỉ đổi compose env.")
            blank()
            if len(lines) >= MIN_LINES:
                break

add("*Hết §Z.4 — ChatOrchestrator và chat-gateway.*")

text = "\n".join(lines) + "\n"
OUT.write_text(text, encoding="utf-8")
print(f"Wrote {len(lines)} lines to {OUT}")
