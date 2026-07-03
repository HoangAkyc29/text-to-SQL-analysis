Lỗ hổng bảo mật (ưu tiên cao)
1.1 ACL role không được truyền xuống sql-gateway khi execute
Pipeline validate SQL với đầy đủ quyền (allowed_tables, denied_columns, store_ids), nhưng khi gọi gateway thì không truyền ACL:
pipeline.py
Lines 280-282
                exec_result = self.sql_gateway.execute_readonly(
                    sanitized, permissions.actor_id, target_db=tdb
                )
Trong khi HttpSqlGatewayClient cũng không hỗ trợ tham số này:
clients.py
Lines 71-75
    def execute_readonly(self, sql: str, actor_id: str, *, target_db: str = "db2") -> dict[str, Any]:
        return self._call(
            "execute_readonly",
            {"sql": sql, "actor_id": actor_id, "target_db": target_db},
        )
Gateway có tham số allowed_tables, nhưng mặc định None = cho phép mọi bảng trong dictionary:
tools_impl.py
Lines 87-99
def execute_readonly(
    sql: str,
    actor_id: str = "system",
    target_db: str = "db1",
    *,
    allowed_tables: list[str] | None = None,
) -> dict[str, Any]:
    ...
    verdict = _policy(actor_id, allowed_tables).validate(sql)
Hệ quả: defense-in-depth bị thủng. Ai gọi trực tiếp sql-gateway (hoặc bypass pipeline) có thể query bảng mà store_manager không được phép, kể cả cột nhạy cảm nếu không bị chặn ở tầng pipeline (vì gateway không biết denied_columns / store_filter).
1.2 explain_sql chạy SQL không qua PolicyEngine
tools_impl.py
Lines 73-81
def explain_sql(sql: str, actor_id: str = "system", target_db: str = "db1") -> dict[str, Any]:
    ...
            cur.execute(f"SET SHOWPLAN_ALL ON; {sql}")
Chỉ có rate limit, không validate trước khi gửi xuống DB. Đây là vector tấn công phụ nếu endpoint bị expose.
1.3 Agent endpoints và MCP tools không có auth
Agent I–IV expose /run công khai, không JWT/mTLS:
app.py
Lines 32-34
@app.post("/run")
def run(request: AgentRequest) -> AgentResponse:
    return get_service().run(request)
Auth chỉ có ở chat-gateway. Trong mạng nội bộ (Docker/K8s) nếu không segment network, bất kỳ service nào cũng có thể giả mạo agent hoặc gọi sql-gateway.
1.4 Python sandbox dùng exec() với open trong builtins
tools_impl.py
Lines 49-57
def run_analysis_script(path: str, script: str, output_dir: str) -> dict[str, Any]:
    ...
    safe_builtins = {"len": len, "str": str, "int": int, "float": float, "range": range, "open": open}
    exec(script, {"__builtins__": safe_builtins}, local_vars)  # noqa: S102
Script do LLM sinh ra có thể đọc file hệ thống, ghi artifact tùy ý. Trên Windows (sys.platform == "win32") CPU limit bị bỏ qua hoàn toàn. Đây không phải sandbox thực sự — chỉ là constraint mềm.
1.5 Dev auth và JWT yếu mặc định
auth.py
Lines 36-39
    if credentials is None:
        if os.getenv("ALLOW_DEV_AUTH") == "1":
            return {"sub": "dev-user", "role": "hq_analyst", "store_ids": None}
ALLOW_DEV_AUTH=1 → full quyền HQ analyst không cần token. JWT_SECRET fallback "change-me-in-production".
2. Khiếm khuyết thiết kế
2.1 Agents khai báo MCP servers nhưng không dùng
platform-supermarket.yaml
Lines 38-50
  sql-planner:
    ...
    mcp_servers: [sql-gateway]  # documented; pipeline invokes sql-gateway
  ...
  data-analyst:
    ...
    mcp_servers: [python-sandbox]  # iv_analyzer + recipe_runtime in pipeline process
Agent không gọi MCP trong ReAct loop; pipeline import trực tiếp python_sandbox.tools_impl. Wiring trong YAML misleading — khó biết ownership thực sự của tool nằm ở đâu.
2.2 Agent là “JSON function” không có contract validation chặt
Pipeline chỉ check chuỗi action:
pipeline.py
Lines 177-180
            if action not in {"plan_sql", "probe_sql"}:
                continue
            sql_queries: list[str] = list(ii_result.get("sql_queries") or [])
Không có Pydantic model cho output Agent II/III/IV. LLM trả JSON sai shape → lỗi runtime hoặc hành vi im lặng (continue), khó debug và không fail-fast.
SupermarketAgentService.json_response chỉ serialize dict, không validate:
supermarket_agent.py
Lines 72-79
    def json_response(ctx: DecisionContext, payload: dict[str, Any]) -> AgentResponse:
        return AgentResponse(
            ...
            payload=payload,
        )
2.3 Risk Reviewer (III) thiếu ngữ cảnh ACL đầy đủ
Agent III chỉ nhận allowed_tables, không có denied_columns, store_ids, store_filter_required:
service.py
Lines 25-29
        allowed_tables = list(payload_in.get("allowed_tables") or meta.get("allowed_tables") or [])
        ...
        policy = PolicyEngine(_CATALOG, allowed_tables=allowed_tables or None)
Pipeline đã validate denied columns trước, nhưng semantic review của LLM không biết cột nào bị cấm → có thể approve query về mặt nghiệp vụ mà vi phạm privacy (dù policy engine pipeline chặn sau). Thiết kế inconsistent giữa các lớp phòng thủ.

2.4 Quy tắc db1/db2 cutoff chỉ nằm trong tài liệu, không enforce trong code
domain_definitions.md mô tả rolling cutoff phức tạp (archive shard theo tháng, UNION cross-db). Không có module tự chọn shard STRANS_YYYYMM hay validate TRAN_DATE vs cutoff. Toàn bộ logic phụ thuộc LLM Agent II chọn đúng target_db và viết SQL đúng — điểm fail cao với domain phức tạp.
2.5 Clarification logic phân tán
Logic clarify nằm ở cả:
ChatOrchestrator (ingress, resume, bridge)
SupermarketAnalysisPipeline (clarify rounds, exploration mode)
Agent I (ingress/clarify/synthesize modes)
Khó reasoning về state machine tổng thể; dễ race condition khi session AWAITING_CLARIFICATION vs pipeline retry.
3. Thiếu sót vận hành & observability
Không có distributed tracing: có trace_id UUID nhưng không propagate qua HTTP calls Agent I–IV
Logging tối thiểu: pipeline gần như silent; sql-gateway không structured log
Không SQL audit log: ai chạy query gì, khi nào, kết quả bao nhiêu row
Không metrics: latency, error rate, LLM cost, gateway queue depth
Health check superficial: {ok: true} — không check Redis/Mongo/DB connectivity
Correlation ID: mỗi lần handle_chat tạo HttpAgentInvoker() mới — không connection pooling, không shared timeout/retry policy
4. Nợ kỹ thuật & anti-patterns
Vấn đề	Chi tiết
Copy trong mỗi agent package — maintenance burden
Silent fallback sql-gateway
HTTP 404 → import in-process, che giấu misconfig
datetime.utcnow()
Deprecated Python 3.12+, dùng rộng rãi
Global MongoClient trong ChatOrchestrator.__init__
Không lifecycle/shutdown, fail silently nếu Mongo down
Tests root tests/
Gần như trống (tests/TODO.md); coverage tập trung project-test
Stub SQL với f-string
ALLOW_LLM_STUB=1 embed user input vào SQL — pattern nguy hiểm nếu copy sang prod
5. Điểm thiết kế tốt (để cân bằng review)
Separation of concerns rõ: gateway = user API, pipeline = state machine, agents = pure decision
Protocol-based clients (AgentInvoker, SqlGatewayClient) — testability tốt với stubs
PolicyEngine có inject TOP/LIMIT, store filter, join depth cap — hướng đúng cho text-to-SQL an toàn
Inbox feedback loop (policy_feedback, risk_feedback, data_feedback) — pattern correction loop hợp lý
Data dictionary as code — agent-facing schema bundle có cap cột/char — tránh context overflow
Role ACL snapshot frozen per analysis trên workflow — audit được permissions tại thời điểm chạy
6. Khuyến nghị ưu tiên
P0 — Trước production
Truyền full ACL snapshot (allowed_tables, denied_columns, store_ids, store_filter_required) xuống mọi lần execute_readonly / explain_sql / validate_sql
Auth trên sql-gateway và agent /run — service token hoặc mTLS nội bộ; không expose ra public network
Thay exec() sandbox bằng subprocess/container với filesystem/network isolation
Validate agent output bằng Pydantic response schemas trước khi pipeline xử lý
P1 — Robustness
Shard/cutoff resolver programmatic cho db1 — không để LLM tự đoán shard name
SQL audit log + propagate trace_id qua tất cả HTTP calls
Enforce max_sync_seconds với deadline trên toàn pipeline
Artifact TTL job theo config/project.yaml
Wire CircuitBreaker vào HttpAgentInvoker / HttpSqlGatewayClient
P2 — Maintainability
Gộp orchestration model — deprecate graph scaffold hoặc tách repo
Cập nhật README/docs phản ánh supermarket domain thực tế
Token tracking thực từ OpenRouter usage metadata
E2E test Redis + Mongo + HTTP agents + security regression (direct gateway bypass)
Kết luận
Repo có nền tảng thiết kế hợp lý cho text-to-SQL enterprise: pipeline deterministic, agents stateless, policy layer có substance. Tuy nhiên, nó đang ở trạng thái “prototype nâng cao” hơn là production-ready:

Lỗ hổng ACL ở sql-gateway là defect thiết kế nghiêm trọng nhất
Sandbox exec() và thiếu auth nội bộ là rủi ro bảo mật thực sự
Nhiều config/abstraction được khai báo nhưng chưa được implement (timeout, TTL, circuit breaker, token budget)
Domain phức tạp (db1/db2 shard, TRANS_CODE) phụ thuộc quá nhiều vào LLM thay vì code hóa invariant nghiệp vụ
Nếu bạn muốn, tôi có thể đi sâu vào một phần cụ thể (ví dụ: fix ACL propagation, thiết kế shard resolver, hoặc hardening sandbox) và implement trực tiếp.
