# Mã nguồn chi tiết: agents và chat-gateway (§Z.2)

Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) (dòng 679–2910).

← [Mục lục docs2](README.md)

---

# Phần Z — Phụ lục: mã nguồn từng tệp

*Phần Z bắt đầu liệt kê chi tiết từng tệp trong repository. Mỗi mục Z.x.y là duy nhất, không lặp lại nội dung các phần trước.*

## §Z.1 — Gốc repository

### Z.1.1 — pyproject.toml (root)

Dòng 1: Khai báo project name `multi-agent-monorepo` version 0.1.0 — đây là workspace root uv, không phải package importable đơn lẻ.

Dòng 7-10: dependencies runtime chỉ gồm platform-core và base-runner — các agent không attach vào root project trực tiếp mà qua workspace members.

Dòng 12-13: workspace members glob bốn cây libs, packages, agents, mcp-servers.

Dòng 60-62: ruff line-length 100, target py311.

Dòng 64-70: pytest testpaths và marker live cho integration DB/LLM thật.

### Z.1.2 — uv.lock

File khóa phiên bản chính xác mọi dependency transitive — reproducible build Docker và CI.

### Z.1.3 — platform-supermarket.yaml

Đăng ký platform id supermarket, trỏ tới config/project.yaml và config/models.yaml.

### Z.1.4 — platform.yaml

Template platform generic — không phải hot path supermarket nếu PLATFORM_CONFIG không trỏ.

### Z.1.5 — docker-compose.yaml

Định nghĩa services redis, mongodb, sql-gateway, 4 agents, chat-gateway.

chat-gateway environment override REDIS_URL và MONGODB_URI sang tên service Docker.

chat-gateway volumes share artifacts, attachments, state với data-analyst.

### Z.1.6 — docker-compose.prod.yaml

Overlay: Redis command requirepass, Mongo MONGO_INITDB_ROOT_*, service caddy, ports chat-gateway empty.

---

---

# Phần Z.2 — Chi tiết mã nguồn agents và chat-gateway (bổ sung)

*Phần này mô tả trực tiếp từ mã nguồn các tệp service.py và app/clients/auth của chat-gateway. Mỗi hàm/phương thức có giải thích tiếng Việt riêng: đầu vào, đầu ra, người gọi, trường hợp biên.*

---

## §Z.2.1 — `agents/conversational-router/src/conversational_router/service.py`

**Vai trò trong hệ thống:** Agent I (conversational-router) là cổng ngôn ngữ tự nhiên đầu tiên trong pipeline phân tích. Tệp này định nghĩa lớp `ConversationalRouterService` kế thừa `SupermarketAgentService`, chịu trách nhiệm phân loại tin nhắn người dùng, tạo `AnalysisBrief`, điều phối làm rõ (clarification), và tổng hợp câu trả lời cuối cho người dùng.

**Đường dẫn đầy đủ:** `agents/conversational-router/src/conversational_router/service.py`

**Số dòng mã nguồn:** 172 dòng (kể cả import và factory).

### Z.2.1.0 — Khối import và phụ thuộc

| Dòng | Import | Ý nghĩa vận hành |
|------|--------|------------------|
| 1 | `from __future__ import annotations` | Cho phép chú thích kiểu forward-reference mà không cần quote string — hỗ trợ type hint trong Python 3.10+. |
| 3 | `import json` | Parse/ghi JSON từ `ctx.request.message` và nội dung LLM trả về. |
| 4 | `import os` | Đọc biến môi trường `ALLOW_LLM_STUB` để chuyển chế độ stub không gọi OpenRouter. |
| 5 | `from pathlib import Path` | Xác định thư mục `skills/` cạnh tệp service khi factory `build_service` khởi tạo. |
| 6 | `from typing import Any` | Kiểu trả về linh hoạt cho `decide()` vì payload JSON đa dạng. |
| 8-9 | `AgentSpec`, `PlatformConfig`, `DecisionContext` | Schema cấu hình platform và ngữ cảnh quyết định từ `platform_core`. |
| 11 | `ClarificationBridge` | Chuyển transcript hội thoại thành câu trả lời làm rõ có cấu trúc. |
| 12-13 | `AnalysisBrief`, `ClarificationRequest` | Hợp đồng dữ liệu domain cho brief phân tích và yêu cầu làm rõ. |
| 14 | `brief_templates_excerpt` | Trích đoạn mẫu brief đưa vào prompt LLM ở chế độ ingress/clarify. |
| 15 | `detect_satisfaction` | Heuristic phát hiện tín hiệu hài lòng/không hài lòng từ văn bản người dùng. |
| 16-18 | `OpenRouterClient`, `agent_profile`, `SupermarketAgentService` | Client LLM, profile model theo agent, lớp cơ sở supermarket. |

**Người gọi import:** Runner agent (`base-runner`) load module qua entry point `build_service`; unit test `packages/project-test/unit/agents/test_agent_I.py` import trực tiếp `ConversationalRouterService`.

### Z.2.1.1 — Lớp `ConversationalRouterService`

**Khai báo:** `class ConversationalRouterService(SupermarketAgentService)` — dòng 21.

**Kế thừa:** Toàn bộ phương thức từ `SupermarketAgentService` (`parse_payload`, `json_response`, `llm_system_prompt`, `resolve_permissions`, `retrieve`, `build_context`) và `BaseAgentService` từ platform. Agent I **không** override các phương thức kế thừa; chỉ triển khai `decide()` và bốn handler nội bộ.

**Khóa agent:** `"I"` — được gán trong `build_service`, dùng bởi `context_policy` khi orchestrator chuyển tiếp quyền.

**Thư mục skills:** `agents/conversational-router/src/conversational_router/skills/` chứa `SKILL.md`, `TOOLS.md`, và các guide markdown (`ingress_guide`, `clarification_bridge_guide`, `clarify_guide`, `synthesize_guide`).

---

### Z.2.1.2 — Phương thức `decide(self, ctx: DecisionContext) -> Any`

**Vị trí mã:** dòng 22–30.

**Mục đích:** Điểm vào duy nhất khi runner gọi Agent I qua HTTP `POST /run`. Phương thức đọc `metadata.mode` để phân nhánh bốn chế độ xử lý khác nhau.

#### Đầu vào

| Tham số / trường | Kiểu | Nguồn | Mô tả |
|------------------|------|-------|-------|
| `self` | `ConversationalRouterService` | — | Instance service đã được inject config, spec, skills. |
| `ctx` | `DecisionContext` | Runner | Bọc `AgentRequest` gồm `session_id`, `actor_id`, `message`, `metadata`. |
| `ctx.request.metadata` | `dict \| None` | Orchestrator / test | Dict tùy chọn; thiếu thì coi như `{}`. |
| `ctx.request.metadata["mode"]` | `str` | Orchestrator | Khóa điều khiển nhánh: `ingress` (mặc định), `clarification_bridge`, `clarify`, `synthesize`. |
| `ctx.request.message` | `str \| None` | Client / orchestrator | Văn bản người dùng hoặc JSON string tùy mode. |

#### Đầu ra

| Nhánh `mode` | Handler gọi | Kiểu trả về |
|--------------|-------------|-------------|
| `"clarification_bridge"` | `_clarification_bridge` | `AgentResponse` qua `json_response` |
| `"clarify"` | `_clarify` | `AgentResponse` |
| `"synthesize"` | `_synthesize` | `AgentResponse` |
| bất kỳ giá trị khác / thiếu | `_ingress` | `AgentResponse` |

Giá trị trả về thực tế là `AgentResponse` từ `SupermarketAgentService.json_response`, có `content` (JSON string) và `payload` (dict).

#### Người gọi (callers)

1. **base-runner HTTP handler** — mọi request tới `AGENT_I_URL/run` cuối cùng gọi `service.decide(ctx)`.
2. **`ChatOrchestrator`** (qua `HttpAgentInvoker.invoke("I", ...)`) — gửi metadata `mode` tương ứng từng giai đoạn pipeline:
   - `ingress` khi người dùng gửi tin nhắn mới.
   - `clarify` khi cần diễn đạt câu hỏi làm rõ.
   - `clarification_bridge` khi người dùng trả lời clarification.
   - `synthesize` sau khi Agent IV hoàn tất phân tích.
3. **Unit test** `test_agent_I.py` — gọi trực tiếp `decide` với `DecisionContext` giả lập.

#### Trường hợp biên (edge cases)

- **`metadata` là `None`:** Biểu thức `(ctx.request.metadata or {})` tránh `AttributeError`; `mode` mặc định `"ingress"`.
- **`mode` không nhận dạng** (ví dụ `"foo"`): Rơi vào nhánh `_ingress` — có thể xử lý sai ý orchestrator nếu typo; không có validation enum.
- **`mode` phân biệt hoa thường:** `"Ingress"` không khớp — sẽ vào `_ingress` vì chỉ so sánh equality chính xác với `"clarification_bridge"`, `"clarify"`, `"synthesize"`.
- **Gọi đồng thời:** Mỗi request độc lập; không có state instance trong `decide` ngoài LLM client tạo trong handler con.

#### Sơ đồ phân nhánh (mô tả văn bản)

```
decide(ctx)
  ├─ mode == "clarification_bridge" → _clarification_bridge(ctx)
  ├─ mode == "clarify"              → _clarify(ctx)
  ├─ mode == "synthesize"           → _synthesize(ctx)
  └─ else (kể cả "ingress")         → _ingress(ctx)
```

---

### Z.2.1.3 — Phương thức `_ingress(self, ctx: DecisionContext)`

**Vị trí mã:** dòng 32–88.

**Mục đích:** Chế độ mặc định — nhận tin nhắn người dùng (và tùy chọn file đính kèm), phân loại `route` (`analysis` vs `chitchat`), tạo `AnalysisBrief` khi cần phân tích, và trả payload JSON cho orchestrator.

#### Đầu vào

| Nguồn | Trường | Mô tả |
|-------|--------|-------|
| `ctx.request.metadata` | `external_sources` | Danh sách dict mô tả file đính kèm đã ingest (text_excerpt, v.v.). |
| `ctx.request.message` | `raw` | Chuỗi plain text hoặc JSON `{"text": "...", "external_sources": [...]}`. |
| Biến môi trường | `ALLOW_LLM_STUB=1` | Bật heuristic stub không gọi OpenRouter. |

#### Xử lý tin nhắn JSON (dòng 37–43)

Nếu `raw.startswith("{")`, thử `json.loads`:
- Thành công: `text = payload.get("text") or raw`; merge `external_sources` từ payload.
- `JSONDecodeError`: Giữ nguyên `raw` làm `text` — tránh crash khi người dùng gõ `{` đầu câu không phải JSON.

#### Phát hiện satisfaction (dòng 44)

`detect_satisfaction(text)` chạy **trước** nhánh stub/LLM — tín hiệu được gắn vào payload đầu ra nếu truthy (dòng 86–87).

#### Nhánh stub `ALLOW_LLM_STUB=1` (dòng 45–63)

**Logic route:** `route = "analysis"` nếu bất kỳ từ khóa nào trong `("vip", "doanh", "bán", "chart", "điểm")` xuất hiện trong `text.lower()`; ngược lại `"chitchat"`.

**Brief stub:** Chỉ khi `route == "analysis"` — tạo `AnalysisBrief(intent=text, metrics=["points"], output_format=["chart"])`.

**External sources trong stub:** Nếu có `external_sources`, validate từng phần tử qua `ExternalSource.model_validate`, gán `brief.external_sources`, và nối excerpt (tối đa 500 ký tự mỗi file) vào `brief.intent`.

**Payload stub:**

```json
{
  "route": "analysis" | "chitchat",
  "user_message": "Đã nhận yêu cầu phân tích." | "Xin chào, tôi có thể giúp gì?",
  "brief": { ... } | null,
  "satisfaction_signal": <kết quả detect_satisfaction hoặc thiếu>
}
```

**Trả về:** `self.json_response(ctx, payload_out)` — không có `usage_tokens`.

#### Nhánh LLM thật (dòng 64–88)

1. Xây `user_content = {"text": text}`; thêm `external_sources` nếu có.
2. `brief_templates_excerpt()` — nếu không rỗng, thêm key `brief_templates_excerpt` vào user message.
3. `OpenRouterClient().chat()` với:
   - `profile_name=agent_profile("router")` — model/temperature từ `config/models.yaml`.
   - System prompt từ `llm_system_prompt(guide="ingress_guide", extra=...)` kèm templates.
   - User message là JSON string `user_content`.
   - `response_format={"type": "json_object"}` — ép LLM trả JSON.
4. `json.loads(result.content)` — **không** bọc try/except: JSON LLM lỗi sẽ raise lên runner.
5. Gắn `satisfaction_signal` nếu `satisfaction` truthy.
6. `json_response(ctx, payload, usage_tokens=result.usage_tokens)`.

#### Đầu ra kỳ vọng (schema orchestrator)

| Khóa | Kiểu | Ý nghĩa |
|------|------|---------|
| `route` | `str` | `"analysis"` kích hoạt pipeline SQL; `"chitchat"` trả lời trực tiếp. |
| `user_message` | `str` | Văn bản hiển thị cho người dùng (có thể song song với brief). |
| `brief` | `object \| null` | `AnalysisBrief` serialized khi `route=analysis`. |
| `satisfaction_signal` | `object \| omitted` | Tín hiệu phản hồi người dùng. |
| `usage_tokens` | `int` | Chỉ khi gọi LLM thật — nằm trong payload qua `json_response`. |

#### Người gọi

- Chỉ được gọi từ `decide()` khi `mode` không phải ba mode đặc biệt.
- Orchestrator gửi `metadata={"mode": "ingress"}` hoặc bỏ `mode`.

#### Trường hợp biên

| Tình huống | Hành vi |
|------------|---------|
| `message` rỗng `""` | `text=""`; stub route thường `chitchat`; LLM vẫn được gọi với text rỗng. |
| `external_sources` không hợp lệ (stub) | `ExternalSource.model_validate` raise — request fail 500. |
| OpenRouter timeout / lỗi mạng | Exception propagate; circuit breaker ở tầng invoker (nếu có). |
| LLM trả JSON thiếu `route` | Orchestrator phải xử lý — service không validate schema đầu ra LLM. |
| Tin nhắn tiếng Việt không dấu khớp keyword stub | Có thể bị phân loại `chitchat` dù ý định phân tích — hạn chế của stub. |

---

### Z.2.1.4 — Phương thức `_clarification_bridge(self, ctx: DecisionContext)`

**Vị trí mã:** dòng 90–117.

**Mục đích:** Sau khi người dùng trả lời câu hỏi làm rõ (clarification), chuyển transcript + `ClarificationRequest` thành cập nhật brief hoặc bước tiếp theo — qua heuristic hoặc LLM.

#### Đầu vào bắt buộc trong metadata

| Khóa | Kiểu | Bắt buộc | Mô tả |
|------|------|----------|-------|
| `clarification_request` | `dict` | Có | Validate thành `ClarificationRequest` — thiếu/sai schema → `ValidationError`. |
| `transcript` | `list` | Không (mặc định `[]`) | Lịch sử lượt hội thoại; phần tử dict hoặc `TranscriptTurn`. |

#### Nhánh stub (dòng 95–99)

- Import lazy `TranscriptTurn` chỉ trong stub.
- Chuẩn hóa từng phần tử transcript: `TranscriptTurn.model_validate(t)` nếu là dict.
- `ClarificationBridge().from_transcript_heuristic(request, turns)` — không gọi LLM.

#### Nhánh LLM (dòng 100–116)

- `ClarificationBridge.parse_llm_bridge(llm.content, request)` parse JSON LLM.
- System guide: `clarification_bridge_guide`.
- User payload: `{"request": request.model_dump(), "transcript": transcript}`.

#### Đầu ra

`json_response(ctx, result.model_dump())` — cấu trúc phụ thuộc `ClarificationBridge` (thường gồm cập nhật brief, `user_message`, hoặc `action`).

#### Người gọi

- `ChatOrchestrator.handle_clarify` — sau khi user POST `/chat/clarify`, orchestrator invoke Agent I với `mode=clarification_bridge`.

#### Trường hợp biên

- **`transcript` rỗng:** Heuristic/LLM vẫn chạy nhưng thiếu ngữ cảnh — có thể sinh brief không đầy đủ.
- **Phần tử transcript không phải dict cũng không phải TranscriptTurn:** Stub path có thể fail validate; LLM path gửi raw list.
- **Thiếu `clarification_request` trong metadata:** `KeyError` hoặc Pydantic validation error khi `model_validate(meta["clarification_request"])`.

---

### Z.2.1.5 — Phương thức `_clarify(self, ctx: DecisionContext)`

**Vị trí mã:** dòng 119–146.

**Mục đích:** Sinh câu hỏi làm rõ thân thiện (`user_message`) từ `ClarificationRequest` có sẵn — thường khi Agent II trả `action: clarify`.

#### Đầu vào

- `meta["clarification_request"]` — bắt buộc, validate `ClarificationRequest`.

#### Nhánh stub (dòng 122–127)

Payload cố định:

```json
{
  "user_message": "Vui lòng chọn thêm thông tin để tiếp tục phân tích.",
  "clarification": <request.model_dump()>
}
```

#### Nhánh LLM (dòng 128–146)

- Guide `clarify_guide` + optional `brief_templates_excerpt` trong system prompt.
- User message = JSON của `request.model_dump()`.
- Sau parse LLM: `payload.setdefault("clarification", request.model_dump())` — đảm bảo orchestrator luôn có bản gốc request.

#### Đầu ra

`AgentResponse` với ít nhất `user_message` và `clarification`.

#### Người gọi

- Orchestrator khi Agent II (hoặc pipeline) yêu cầu hiển thị clarification UI — invoke với `metadata.mode="clarify"`.

#### Trường hợp biên

- LLM trả thiếu `user_message`: Orchestrator/UI có thể hiển thị trống — service không fallback.
- `clarification_request.questions` rỗng: LLM vẫn được hỏi — chất lượng câu hỏi phụ thuộc model.

---

### Z.2.1.6 — Phương thức `_synthesize(self, ctx: DecisionContext)`

**Vị trí mã:** dòng 148–166.

**Mục đích:** Tổng hợp kết quả kỹ thuật từ Agent IV thành câu trả lời tự nhiên cho người dùng cuối pipeline.

#### Đầu vào

- `meta.get("technical_summary") or {}` — dict tóm tắt do orchestrator/pipeline đính kèm; thường gồm `outcome`, `artifact_urls`, số liệu, lỗi.

#### Nhánh stub (dòng 151–156)

```json
{
  "user_message": "Kết quả: {outcome}.",
  "artifacts": <artifact_urls hoặc []>
}
```

`outcome` mặc định chuỗi `"done"` nếu thiếu.

#### Nhánh LLM (dòng 157–166)

- Guide `synthesize_guide`.
- User content = toàn bộ `summary` JSON.
- Trả thẳng `json.loads(result.content)` — không merge thêm field bắt buộc.

#### Người gọi

- Orchestrator sau bước `analyze_datasets` thành công hoặc một phần — `mode=synthesize`.

#### Trường hợp biên

- `technical_summary` rỗng: Stub vẫn trả `"Kết quả: done."`; LLM nhận `{}` — câu trả lời có thể chung chung.
- LLM không trả `artifacts` dù summary có URL: Client có thể mất link tải — orchestrator nên giữ artifact ở tầng session.

---

### Z.2.1.7 — Hàm `build_service(config, spec) -> ConversationalRouterService`

**Vị trí mã:** dòng 169–171.

**Mục đích:** Factory entry point cho agent runner — đăng ký trong cấu hình platform/agent manifest.

#### Đầu vào

| Tham số | Kiểu | Nguồn |
|---------|------|-------|
| `config` | `PlatformConfig` | Loader đọc `platform-supermarket.yaml` + `project.yaml`. |
| `spec` | `AgentSpec` | Metadata agent I trong config (port, name). |

#### Đầu ra

Instance `ConversationalRouterService` với:
- `skills_root = Path(__file__).parent / "skills"`
- `agent_key="I"`
- **Không** inject `retriever` — Agent I không dùng Mongo retrieval trong factory này.

#### Người gọi

- Module hook khi uvicorn/agent process khởi động conversational-router container.
- Test có thể gọi trực tiếp để có service đầy đủ skills.

#### Trường hợp biên

- Thư mục `skills/` thiếu file guide: `llm_system_prompt` fallback chuỗi generic `"You are supermarket agent I..."`.

## §Z.2.2 — `agents/sql-planner/src/sql_planner/service.py`

**Vai trò:** Agent II (sql-planner) chuyển `AnalysisBrief` + ngữ cảnh schema thành danh sách câu SQL readonly, yêu cầu làm rõ, hoặc probe SQL khi dữ liệu phản hồi từ Agent IV.

**Số dòng mã nguồn:** 280 dòng.

### Z.2.2.0 — Import đặc thù Agent II

| Import | Vai trò |
|--------|---------|
| `apply_data_feedback` | Merge phản hồi dữ liệu từ IV vào brief trước khi lập kế hoạch SQL. |
| `DataFeedback` | Validate cấu trúc `inbox.data_feedback` trong `_probe_plan`. |
| `resolve_product_code` | Sinh probe SQL và predicate SKU khi brief có `product_code`/`sku`. |
| `try_create_hybrid_retriever` | Factory Mongo hybrid retriever — chỉ dùng trong `build_service`. |

### Z.2.2.1 — Lớp `SqlPlannerService`

Kế thừa `SupermarketAgentService` với `agent_key="II"`. Có thể có `self.retriever` (Mongo) để bổ sung `retrieval_context` khi orchestrator không gửi sẵn.

---

### Z.2.2.2 — Phương thức `decide(self, ctx: DecisionContext) -> Any`

**Vị trí mã:** dòng 22–76.

**Mục đích:** Điểm vào Agent II — parse payload, kiểm tra quyền `validate_sql`, áp dụng data feedback, retrieval, rồi gọi LLM hoặc stub plan.

#### Bước 1 — Parse đầu vào (dòng 23–28)

Gọi `self.parse_payload(ctx)` → `(payload_in, meta)`.

| Trường | Nguồn ưu tiên | Mặc định |
|--------|---------------|----------|
| `brief` | `payload_in["brief"]` hoặc `meta["brief"]` | `{}` → validate `AnalysisBrief` |
| `inbox` | payload hoặc meta | `{}` |
| `attempt` | payload hoặc meta | `1` (ép `int`) |
| `schema_context` | payload hoặc meta | `{}` |
| `retrieval_context` | payload hoặc meta | `[]` |

`AnalysisBrief.model_validate(...)` — brief rỗng `{}` vẫn tạo object với field default Pydantic.

#### Bước 2 — Kiểm tra quyền (dòng 30–37)

```python
permissions = self.resolve_permissions(payload_in, meta)
if permissions is None or not self.context_policy.can_invoke_tool(permissions, "II", "validate_sql"):
    return json_response(ctx, {"action": "impossible", "reason": "tool_not_granted:validate_sql"})
```

**Fail-closed:** Thiếu `PermissionsSnapshot` hoặc không có capability `validate_sql` cho agent II → không lập SQL.

**Người chịu trách nhiệm gửi permissions:** `ChatOrchestrator` / pipeline chèn snapshot từ `load_effective_permissions`.

#### Bước 3 — Retrieval bổ sung (dòng 39–41)

Chỉ khi `retrieval_context` rỗng **và** `self.retriever` khác `None`:

```python
chunks = self.retrieve(brief.intent, top_k=5)
retrieval_context = [c.text for c in chunks]
```

**Edge:** Retriever lỗi Mongo — exception từ `retrieve()` propagate.

#### Bước 4 — Data feedback (dòng 43–44)

Nếu `inbox.get("data_feedback")` truthy → `brief = apply_data_feedback(brief, inbox["data_feedback"])`.

Có thể thay đổi filters, exploration_mode, v.v. trước khi plan.

#### Bước 5 — Stub vs LLM (dòng 46–76)

- `ALLOW_LLM_STUB=1` → `_stub_plan(...)`.
- Ngược lại: nếu `inbox` có `probe_mode` hoặc `data_feedback`, đọc guide `probe_feedback_guide` làm `extra` system prompt.
- LLM profile `agent_profile("sql_planner")`, guide `plan_sql_guide`.
- User JSON gồm: `brief`, `inbox`, `attempt`, `schema_context`, `retrieval_context`.
- Trả `json.loads(result.content)` không validate schema.

#### Đầu ra có thể

| `action` | Ý nghĩa |
|----------|---------|
| `impossible` | Không đủ quyền |
| `clarify` | Cần người dùng chọn (stub VIP) |
| `plan_sql` | Danh sách SQL chính |
| `probe_sql` | SQL khám phá từ data feedback |
| (LLM tự định nghĩa) | Model có thể trả key khác — orchestrator phải tolerant |

#### Người gọi

- `HttpAgentInvoker.invoke("II", payload, metadata)` từ `SupermarketAnalysisPipeline`.
- Unit test `test_agent_II.py`.

#### Trường hợp biên tổng hợp

| Tình huống | Kết quả |
|------------|---------|
| `attempt` không phải số | `int()` có thể raise `ValueError`. |
| `brief` JSON sai schema | Pydantic `ValidationError` tại `model_validate`. |
| `retrieval_context` đã có từ orchestrator | Không gọi retriever dù instance có Mongo. |
| LLM trả SQL nguy hiểm | Agent III mới review — II không tự validate policy. |

---

### Z.2.2.3 — Phương thức `_stub_plan(self, ctx, brief, inbox, attempt, schema_context)`

**Vị trí mã:** dòng 78–212.

**Mục đích:** Kế hoạch SQL deterministic cho test/local khi `ALLOW_LLM_STUB=1` — mô phỏng các nhánh nghiệp vụ siêu thị phổ biến.

#### Tham số

| Tham số | Kiểu | Ghi chú |
|---------|------|---------|
| `ctx` | `DecisionContext` | Cho `json_response`. |
| `brief` | `AnalysisBrief` | Đã qua feedback merge. |
| `inbox` | `dict` | Chứa `probe_mode`, `data_feedback`. |
| `attempt` | `int` | Lần thử pipeline (ảnh hưởng grain retry). |
| `schema_context` | `dict` | **Không dùng** trong thân stub hiện tại — tham số dự phòng API. |

#### Nhánh probe đầu tiên (dòng 88–91)

Nếu `inbox.probe_mode` hoặc `inbox.data_feedback` → gọi `_probe_plan`; nếu trả dict khác `None`, return ngay.

#### Nhánh clarify VIP (dòng 93–127)

Điều kiện **đồng thời**:

1. `attempt == 1`
2. `not brief.exploration_mode`
3. `not filters.get("card_prefix")`
4. `"vip" in brief.intent.lower()`

Tạo `ClarificationRequest` với `reason="missing_vip_definition"` và 3 lựa chọn: prefix E, tier VIP, unknown/explore.

**Edge:** Intent `"VIP"` uppercase vẫn khớp vì `.lower()`. Intent tiếng Việt không chữ "vip" bỏ qua nhánh này.

#### Nhánh decomposed plan (dòng 129–130)

Nếu `brief.plan.is_decomposed` và `len(subtasks) > 1` → `_plan_for_subtasks`.

**Edge:** `brief.plan` None → short-circuit falsy, không vào nhánh.

#### Nhánh product code (dòng 132–150)

`product_code = filters.get("product_code") or filters.get("sku")`.

`resolve_product_code(str(product_code))`:
- Append mọi `resolved.probe_sql` với meta `role=probe`, `purpose=product_lookup`, db `db2`.
- Câu main: `SUM(AMOUNT)` từ `STRANS` `TRANS_CODE='113'` với predicate từ candidate tốt nhất hoặc fallback `SKU_ID = '...'`.

#### Nhánh exploration (dòng 151–171)

Khi `brief.exploration_mode` hoặc `user_knowledge_level == "unknown"`:

3 câu SQL: monthly trend, by store, SKU sample từ `SKU_DEF`.

#### Nhánh mặc định VIP/revenue (dòng 172–185)

2 câu: CSCARD+PMTRANS (`TRANS_CODE='221'`) và monthly STRANS.

#### Nhánh grain feedback (dòng 187–198)

Nếu `inbox.data_feedback` và `issue == "grain"` và `attempt > 1`:

Thay toàn bộ bằng 1 câu line-level `TRANS_NUM, SKU_ID, AMOUNT, QTY`.

**Edge:** `data_feedback` là dict thô không qua `DataFeedback` model ở đây — chỉ đọc `issue` key.

#### Payload trả về chuẩn `plan_sql` (dòng 200–212)

Luôn gồm: `sql_queries`, `query_meta`, `target_dbs`, `target_db="db2"`, `reasoning`, `attempt`, `schema_tables_used`.

---

### Z.2.2.4 — Phương thức `_probe_plan(self, brief, inbox) -> dict | None`

**Vị trí mã:** dòng 214–229.

**Mục đích:** Chuyển `DataFeedback.probe_requests` thành action `probe_sql` tối đa 3 câu.

#### Đầu vào

- `inbox["data_feedback"]` — raw dict.

#### Xử lý

1. `DataFeedback.model_validate(raw)` — bất kỳ `Exception` → return `None` (nuốt lỗi).
2. Nếu `not fb.probe_requests` → `None`.
3. Lấy tối đa 3 phần tử đầu: `suggested_sql`, `purpose` cho meta.

#### Đầu ra khi thành công

```python
{
  "action": "probe_sql",
  "sql_queries": [...],
  "query_meta": [{"role": "probe", "purpose": p.purpose}, ...],
  "target_dbs": ["db2"] * len(sql),
  "reasoning": "IV-requested probe SQL",
}
```

#### Người gọi

- Chỉ `_stub_plan` — LLM path không gọi hàm này trực tiếp (LLM tự sinh probe trong JSON).

#### Trường hợp biên

- `data_feedback` malformed: Im lặng return `None` — stub tiếp tục nhánh plan thường.
- Hơn 3 probe requests: Cắt slice `[:3]` — phần còn lại bỏ qua.
- `suggested_sql` rỗng: Vẫn đưa vào list — III/gateway sẽ reject.

---

### Z.2.2.5 — Phương thức `_plan_for_subtasks(self, brief, attempt) -> dict`

**Vị trí mã:** dòng 231–271.

**Mục đích:** Mỗi `subtask` trong `brief.plan.subtasks` sinh một câu SQL theo keyword intent.

#### Phân loại subtask (dòng 236–260)

| Điều kiện intent (lower) | SQL | purpose |
|--------------------------|-----|---------|
| `"inventory"` hoặc `"tồ"` | `STK_DTL` QTY_ONHAND | inventory |
| `"vip"` | CSCARD+PMTRANS | vip_revenue |
| `"trend"`, `"tháng"`, `"month"` | STRANS monthly | monthly_trend |
| else | STRANS by STK_ID | revenue |

Mỗi meta có `subtask_id` từ `subtask.id`.

#### Assert (dòng 235)

`assert brief.plan is not None` — caller đảm bảo; vi phạm → `AssertionError` trong dev.

#### Đầu ra

Dict `plan_sql` với `reasoning=f"Decomposed plan with {len(sql)} subtasks"`.

#### Trường hợp biên

- Subtask intent đa ngôn ngữ không khớp keyword: Rơi nhánh `else` revenue-by-store — có thể không đúng ý.
- Nhiều subtask cùng loại: Nhiều câu SQL trùng pattern — gateway chạy tuần tự.
- `subtask.id` thiếu: Meta `subtask_id` có thể null tùy model Pydantic.

---

### Z.2.2.6 — Hàm `build_service(config, spec) -> SqlPlannerService`

**Vị trí mã:** dòng 274–279.

**Khác Agent I:** Gọi `try_create_hybrid_retriever()` — trả `None` nếu Mongo không cấu hình, service vẫn chạy không retrieval.

**Đầu ra:** `SqlPlannerService(..., agent_key="II", retriever=retriever)`.

**Người gọi:** Agent II process entry point.


## §Z.2.3 — `agents/risk-reviewer/src/risk_reviewer/service.py`

**Vai trò:** Agent III đánh giá rủi ro câu SQL trước khi sql-gateway thực thi — kết hợp `PolicyEngine` deterministic và (tùy chế độ) LLM semantic review.

**Hằng số module:** `_CATALOG = SchemaCatalog.from_dictionary_dir()` — load một lần khi import module; dùng chung mọi request.

### Z.2.3.1 — Lớp `RiskReviewerService`

`agent_key="III"`. Không có retriever. Skills guide chính: `review_guide`.

---

### Z.2.3.2 — Phương thức `decide(self, ctx: DecisionContext) -> Any`

**Vị trí mã:** dòng 21–122.

#### Parse đầu vào (dòng 22–30)

| Trường | Nguồn | Ghi chú |
|--------|-------|---------|
| `sql` | payload hoặc meta | Chuỗi SQL đầy đủ một câu |
| `allowed_tables` | payload hoặc meta | List tên bảng ACL — có thể rỗng |
| `denied_columns` | payload hoặc meta | Cột cấm |
| `store_ids` | payload nếu key có, else meta | `None` nghĩa là không giới hạn store |
| `store_filter_required` | payload hoặc meta, default `False` | Bắt buộc predicate store |
| `schema_context` | payload hoặc meta | Ngữ cảnh bảng cho LLM |

**Edge `store_ids`:** Dùng `"store_ids" in payload_in` — phân biệt key thiếu vs key explicit `null`.

#### Kiểm tra quyền (dòng 32–44)

Cho phép nếu **một trong hai**:

- `cp.can_execute_sql(permissions)`
- `cp.can_invoke_tool(permissions, "III", "explain_sql")`

Nếu không → `verdict: reject`, `concerns: ["tool_not_granted:sql-gateway"]`, `risk_feedback.issue: tool_not_granted`.

**Thiết kế:** Quyền execute SQL hoặc tool explain đều đủ để agent III tham gia pipeline.

#### PolicyEngine (dòng 46–53)

```python
policy = PolicyEngine(
    _CATALOG,
    allowed_tables=allowed_tables or None,
    denied_columns=denied_columns or None,
    store_ids=store_ids,
    store_filter_required=store_filter_required,
)
verdict = policy.validate(sql)
```

List rỗng `[]` chuyển thành `None` — engine dùng default catalog đầy đủ.

#### Nhánh stub `ALLOW_LLM_STUB=1` (dòng 55–72)

`blocked` khi:

- `not verdict.allowed`, **hoặc**
- Token nguy hiểm trong SQL lower: `drop`, `delete`, `insert`, `update`, `exec ` (có space sau exec).

`concerns` = `verdict.violations`; nếu blocked mà violations rỗng → `["forbidden_statement"]`.

`needs_explain`: `True` nếu blocked và có concern chứa substring `"scan"` (case trong concern string).

Luôn đính `schema_context_summary` với `table_count` và `has_domain_definitions`.

#### Nhánh policy reject (không stub, dòng 74–89)

Không gọi LLM. Trả reject với `risk_feedback.suggestion` cố định tiếng Anh hướng dẫn sửa SQL.

#### Nhánh LLM approve path (dòng 91–122)

Chỉ khi `verdict.allowed` và không stub.

Gửi LLM: sql, ACL fields, schema_context, và `policy_result` snapshot.

Sau parse:

- `setdefault` `schema_context_summary`.
- Nếu `verdict == "reject"` mà thiếu `risk_feedback` → tạo từ `concerns[0]` hoặc `"semantic_risk"`.

**Edge:** LLM có thể reject dù policy approve — pipeline phải tôn trọng `verdict` JSON LLM.

#### Người gọi

- Pipeline invoke Agent III cho từng câu SQL trước `execute_readonly`.
- `test_agent_III.py`.

#### Ma trận kết quả

| policy | stub/LLM | verdict điển hình |
|--------|----------|-------------------|
| deny | stub | reject + violations |
| allow | stub + token DROP | reject forbidden |
| allow | stub clean | approve |
| deny | LLM không gọi | reject |
| allow | LLM | approve/reject tùy model |

---

### Z.2.3.3 — Hàm `build_service(config, spec) -> RiskReviewerService`

**Vị trí mã:** dòng 125–127.

`skills_root` cạnh file, `agent_key="III"`, không retriever.

**Edge:** Import module load `_CATALOG` — khởi động chậm hơn nếu dictionary_dir lớn; lỗi thiếu thư mục dictionary fail tại import.

---

## §Z.2.4 — `agents/data-analyst/src/data_analyst/service.py`

**Vai trò:** Agent IV — wrapper mỏng quanh `analyze_datasets` (iv_analyzer): chạy pandas/plot trong sandbox, sinh artifact, data_feedback.

### Z.2.4.1 — Lớp `DataAnalystService`

Không override `SupermarketAgentService` ngoài `skill_reference` và `decide`.

---

### Z.2.4.2 — Phương thức `skill_reference(self) -> str`

**Vị trí mã:** dòng 16–18.

**Mục đích:** Expose nội dung system prompt phân tích (`analyze_guide`) cho tooling và test — không tham gia pipeline HTTP thông thường.

**Đầu ra:** Chuỗi markdown ghép từ SKILL + TOOLS + guide.

**Người gọi:** Unit test Agent IV; có thể CLI debug.

**Edge:** `self.skill` None → fallback generic agent IV string từ `llm_system_prompt`.

---

### Z.2.4.3 — Phương thức `decide(self, ctx: DecisionContext) -> Any`

**Vị trí mã:** dòng 20–75.

#### Parse trường (dòng 21–34)

| Trường | Mặc định | Ý nghĩa |
|--------|----------|---------|
| `dataset_manifest` | `{}` | Danh sách parquet/path từ sql-gateway |
| `result_profile` | `{}` | Thống kê cột, grain, row count |
| `brief` | `{}` | AnalysisBrief |
| `query_meta` | `[]` | Meta từng câu SQL II |
| `out_dir` | `"data/artifacts/out"` | Thư mục ghi chart/csv |
| `max_steps` | `load_project_config().pipeline.iv_max_steps` | Giới hạn bước phân tích |
| `analysis_tools` | `[]` | Tool registry candidates |
| `recipe_candidates` | `[]` | Công thức phân tích gợi ý |

`max_steps` ưu tiên payload → meta → config YAML.

#### Kiểm tra quyền (dòng 36–51)

`can_invoke_tool(permissions, "IV", "run_analysis_script")` — thiếu → action `data_feedback` với `issue: tool_not_granted`, `impossible_reason: tool_not_granted:python-sandbox:run_analysis_script`.

**Không raise HTTP 403** — trả JSON để pipeline xử lý graceful.

#### Lọc recipe (dòng 52–56)

List comprehension giữ candidate nếu không có `tool_id` hoặc `can_invoke_function(permissions, tool_id)`.

**Edge:** Candidate thiếu quyền bị loại im lặng — có thể còn 0 recipe.

#### Trường tùy chọn bổ sung (dòng 58–60)

`analysis_plan`, `execution_plan`, `domain_rules_excerpt` — chuyển thẳng vào `analyze_datasets`.

#### Gọi core (dòng 62–75)

```python
payload = analyze_datasets(
    brief=brief,
    manifest=manifest,
    profile=profile,
    out_dir=out_dir,
    max_steps=max_steps,
    query_meta=query_meta,
    analysis_tools=analysis_tools,
    recipe_candidates=recipe_candidates,
    analysis_plan=analysis_plan,
    execution_plan=execution_plan,
    domain_rules_excerpt=domain_rules_excerpt,
)
return self.json_response(ctx, payload)
```

**Logic nặng nằm trong `iv_analyzer`** — service không try/except; lỗi sandbox propagate.

#### Đầu ra điển hình từ `analyze_datasets`

| action | Khi nào |
|--------|---------|
| `complete` | Phân tích xong có artifact |
| `data_feedback` | Cần SQL lại / grain sai |
| `impossible` | Dữ liệu không đủ |

#### Người gọi

- Pipeline bước IV sau khi có manifest parquet.
- `test_agent_IV.py`.

#### Trường hợp biên

| Tình huống | Hành vi |
|------------|---------|
| `manifest` rỗng | `analyze_datasets` quyết định feedback — service không guard |
| `out_dir` không writable | Lỗi OS từ sandbox |
| `brief` invalid | Pydantic ValidationError tại dòng 25 |
| permissions None | Fail-closed tool_not_granted |

---

### Z.2.4.4 — Hàm `build_service(config, spec) -> DataAnalystService`

**Vị trí mã:** dòng 78–80.

Giống Agent I/III — không retriever. `agent_key="IV"`.


## §Z.2.5 — `agents/chat-gateway/src/chat_gateway/app.py`

**Vai trò:** FastAPI application — cổng HTTP duy nhất cho UI/client: health, auth, chat, clarify, upload, feedback, artifact download.

**Khởi động:** `load_project_env()` dòng 20 — nạp `.env` trước khi import orchestrator.

**Biến toàn cục:** `_orchestrator: ChatOrchestrator | None = None` — lazy singleton.

---

### Z.2.5.0 — Import và phụ thuộc app.py

| Dòng | Symbol | Vai trò |
|------|--------|---------|
| 7 | FastAPI, Depends, File, HTTPException, UploadFile | Web framework và dependency injection |
| 8 | FileResponse, JSONResponse | Trả file artifact và JSON lỗi tùy chỉnh |
| 12-13 | ClarificationReply, FeedbackRecord | Schema body clarify/feedback |
| 14 | PermissionsUnavailableError | Exception domain khi AUTH DB permissions fail |
| 15 | ingest_file | Parse upload thành ExternalSource |
| 17-18 | current_user, issue_token, ChatOrchestrator | Auth và điều phối pipeline |

---

### Z.2.5.1 — Exception handler `_permissions_unavailable_handler`

**Vị trí mã:** dòng 25–32.

**Chữ ký:** `async def _permissions_unavailable_handler(_request: Request, exc: PermissionsUnavailableError) -> JSONResponse`

**Đăng ký:** `@app.exception_handler(PermissionsUnavailableError)` — FastAPI bắt exception này toàn app.

#### Đầu vào

| Tham số | Mô tả |
|---------|-------|
| `_request` | Request HTTP — không dùng trong handler |
| `exc` | Exception có thuộc tính `.code` |

#### Đầu ra

HTTP 403 JSON: `{"detail": "permissions_unavailable", "code": <exc.code>}`.

#### Người gọi

- FastAPI runtime khi route/orchestrator raise `PermissionsUnavailableError` — thường từ pipeline khi `load_effective_permissions` trả `None` ngoài dev mode.

#### Trường hợp biên

- Handler async nhưng logic đồng bộ — vẫn hợp lệ với FastAPI.
- Exception khác (HTTPException 401) không đi qua handler này.

---

### Z.2.5.2 — Hàm `get_orchestrator() -> ChatOrchestrator`

**Vị trí mã:** dòng 36–40.

**Mục đích:** Lazy-init singleton orchestrator — tránh khởi tạo nặng (Redis, Mongo, HTTP pool) khi chỉ gọi `/health/live`.

#### Đầu vào

Không có tham số.

#### Đầu ra

Instance `ChatOrchestrator` — tạo mới lần đầu, tái sử dụng sau.

#### Người gọi

Hầu hết route handlers: `health`, `health_ready`, `chat`, `upload_attachment`, `feedback`, `get_artifact`, v.v.

#### Trường hợp biên

| Tình huống | Hành vi |
|------------|---------|
| Gọi đồng thời lần đầu | Có thể race tạo 2 orchestrator trên một số server — hiếm với uvicorn single worker |
| `ChatOrchestrator()` raise | Process fail tại request đầu tiên cần orchestrator |
| Test monkeypatch | Cần reset `_orchestrator = None` giữa test nếu đổi wiring |

---

### Z.2.5.3 — Pydantic request models

#### Z.2.5.3.1 — `ChatRequest` (dòng 43–45)

| Field | Kiểu | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `session_id` | `str` | Có | Khóa phiên Redis/STM |
| `message` | `str` | Có | Tin nhắn người dùng plain text |

**Người gọi:** Body POST `/chat`.

**Edge:** `session_id` rỗng — orchestrator vẫn chạy nhưng state có thể collision.

#### Z.2.5.3.2 — `ClarifyRequest` (dòng 48–50)

| Field | Kiểu | Mô tả |
|-------|------|-------|
| `session_id` | `str` | Phiên đang chờ clarification |
| `reply` | `ClarificationReply` | Câu trả lời có cấu trúc (question_id, option_id, ...) |

**Người gọi:** POST `/chat/clarify`.

#### Z.2.5.3.3 — `FeedbackRequest` (dòng 53–58)

| Field | Kiểu | Mô tả |
|-------|------|-------|
| `session_id` | `str` | Phiên phân tích |
| `analysis_id` | `str` | ID phân tích pipeline |
| `trace_id` | `str` | Trace OpenTelemetry / artifact folder |
| `sentiment` | `str` | `"positive"` / `"negative"` / ... |
| `comment` | `str \| None` | Ghi chú tùy chọn |

**Edge:** `sentiment` không validate enum tại model — Mongo ghi raw string.

#### Z.2.5.3.4 — `DomainRuleConfirmRequest` (dòng 61–63)

| Field | Default | Mô tả |
|-------|---------|-------|
| `rule_id` | — | ID quy tắc domain cần xác nhận |
| `confirmed` | `True` | User đồng ý hay từ chối |

#### Z.2.5.3.5 — `DevLoginRequest` (dòng 66–68)

| Field | Default | Mô tả |
|-------|---------|-------|
| `actor_id` | `"dev-user"` | JWT `sub` |
| `role` | `"hq_analyst"` | JWT `role` |

#### Z.2.5.3.6 — `LoginRequest` (dòng 71–73)

| Field | Mô tả |
|-------|-------|
| `username` | Đăng nhập AUTH DB |
| `password` | Plain text — verify bcrypt server-side |

---

### Z.2.5.4 — Route `GET /health`

**Vị trí mã:** dòng 76–78.

**Handler:** `def health() -> dict`

#### Đầu ra

```json
{"ok": true, "redis": true, "mongo": <bool>, "agents": {}}
```

**Lưu ý:** `redis` **luôn** `True` — không ping thật. `mongo` = `orch.feedback is not None`. `agents` dict rỗng cố định.

#### Người gọi

- Load balancer shallow check — **không** đại diện sức khỏe thật.

#### Edge

Misleading nếu Redis down — dùng `/health/ready` cho probe thật.

---

### Z.2.5.5 — Route `GET /health/live`

**Vị trí mã:** dòng 81–83.

**Đầu ra:** `{"ok": True}` — process còn sống.

**Người gọi:** Kubernetes livenessProbe.

**Edge:** Không kiểm tra dependency — luôn 200 nếu process chạy.

---

### Z.2.5.6 — Route `GET /health/ready`

**Vị trí mã:** dòng 86–104.

**Handler:** `def health_ready() -> dict`

#### Logic chi tiết

1. `orch = get_orchestrator()`.
2. Với mỗi `(key, url)` trong `orch.pipeline.agent_invoker.urls`:
   - `httpx.get(f"{url}/health", timeout=2.0)`.
   - `agents[key] = "ok"` nếu status 200 else `"error"`.
   - Exception bất kỳ → `"error"`.
3. Redis: `orch.stm.client.ping()` — exception → `redis_ok = False`.
4. Mongo: `orch.feedback is not None` (không ping deep).
5. `ok = redis_ok and mongo_ok` — **không** yêu cầu tất cả agents ok.

#### Đầu ra

```json
{"ok": <bool>, "redis": <bool>, "mongo": <bool>, "agents": {"I": "ok"|"error", ...}}
```

#### Người gọi

- Kubernetes readinessProbe.
- Monitoring dashboard.

#### Trường hợp biên

| Tình huống | Ảnh hưởng |
|------------|-----------|
| Một agent down | `agents` ghi error nhưng `ok` vẫn có thể True nếu redis+mongo ok |
| `agent_invoker` không có `.urls` | AttributeError — type ignore comment cho thấy coupling pipeline |
| httpx import lazy | Chỉ load khi gọi ready |

---

### Z.2.5.7 — Route `POST /auth/dev-login`

**Vị trí mã:** dòng 107–112.

**Handler:** `def dev_login(body: DevLoginRequest) -> dict[str, str]`

#### Đầu vào

Body JSON `DevLoginRequest`.

#### Kiểm tra

`ALLOW_DEV_AUTH != "1"` → HTTP 403 `dev_auth_disabled`.

#### Đầu ra thành công

```json
{"access_token": "<jwt>", "token_type": "bearer"}
```

Token từ `issue_token(body.actor_id, body.role)` — **không** có `store_ids` trong dev login.

#### Người gọi

- Frontend dev, integration test `test_auth_login.py`.

#### Edge

- Production nếu quên tắt `ALLOW_DEV_AUTH` — lỗ hổng auth bypass password.
- Role tùy ý client gửi — không validate với DB.

---

### Z.2.5.8 — Route `POST /auth/login`

**Vị trí mã:** dòng 115–128.

**Handler:** `def login(body: LoginRequest) -> dict[str, str]`

#### Luồng

1. Lazy import `authenticate` từ `auth_store`.
2. `user = authenticate(username, password)`.
3. `None` → HTTP 401 `invalid_credentials`.
4. `issue_token(user.user_id, user.role, user.store_ids)`.

#### Đầu ra thành công

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "role": "...",
  "display_name": "..."
}
```

#### Người gọi

- UI đăng nhập production.

#### Edge

| Tình huống | Hành vi |
|------------|---------|
| AUTH_DB down | `authenticate` return None → 401 (không lộ DB error) |
| User inactive | Không có row → 401 |
| Timing attack | Không constant-time — ngoài phạm vi app |

---

### Z.2.5.9 — Route `GET /auth/login` (OAuth redirect)

**Vị trí mã:** dòng 131–137.

**Handler:** `def oauth_login() -> dict[str, str]`

#### Đầu ra

`{"authorization_url": "<url>"}` từ `oauth_provider_from_env().authorization_url("dev")`.

**State cố định `"dev"`** — không phải CSRF token ngẫu nhiên production-grade.

#### Người gọi

- SPA bắt đầu OAuth flow.

#### Edge

- Provider chưa cấu hình env — lỗi từ oauth module.

---

### Z.2.5.10 — Route `GET /auth/callback`

**Vị trí mã:** dòng 140–144.

**Handler:** `def oauth_callback(code: str) -> dict[str, Any]`

**Query param:** `code` — authorization code từ IdP.

**Đầu ra:** Kết quả `exchange_code(code)` — thường gồm `access_token`.

#### Edge

- Thiếu `code` → FastAPI 422 validation error.
- Code hết hạn — lỗi từ provider.

---

### Z.2.5.11 — Route `POST /chat`

**Vị trí mã:** dòng 147–150.

**Handler:** `def chat(body: ChatRequest, user: dict = Depends(current_user)) -> dict`

#### Đầu vào

- Body: `session_id`, `message`.
- `user` claims JWT: `sub`, `role`, `store_ids`.

#### Xử lý

`get_orchestrator().handle_chat(session_id=..., message=..., user=user)` → `resp.model_dump()`.

#### Đầu ra

Dict response orchestrator — thường gồm `user_message`, `route`, `analysis_id`, `clarification`, artifact refs.

#### Người gọi

- Frontend chat chính.

#### Trường hợp biên

| Tình huống | Hành vi |
|------------|---------|
| Không token + không ALLOW_DEV_AUTH | 401 missing_token |
| Permissions unavailable | 403 qua exception handler |
| Pipeline timeout 120s | httpx timeout từ invoker |

---

### Z.2.5.12 — Route `POST /chat/clarify`

**Vị trí mã:** dòng 153–156.

**Handler:** `def chat_clarify(body: ClarifyRequest, user = Depends(current_user))`

Gọi `handle_clarify(session_id, reply, user)`.

#### Edge

- Session không tồn tại / hết hạn — orchestrator quyết định lỗi.
- Reply không khớp question_id — bridge Agent I xử lý.

---

### Z.2.5.13 — Route `POST /attachments`

**Vị trí mã:** dòng 159–174.

**Handler:** `async def upload_attachment(session_id, file: UploadFile, user)`

#### Tham số

| Nguồn | Tên | Kiểu |
|-------|-----|------|
| Query/form | `session_id` | `str` |
| Multipart | `file` | `UploadFile` |

#### Luồng

1. `content = await file.read()`.
2. `len(content) > 20 * 1024 * 1024` → HTTP 413 `file_too_large`.
3. `ingest_file(session_id, filename, content)` → `ExternalSource`.
4. `attach_external_sources(session_id, [source.model_dump()])`.
5. Trả `{"status": "ok", "source": ...}`.

#### Người gọi

- UI upload CSV/Excel/PDF trước khi chat.

#### Edge

| Tình huống | Hành vi |
|------------|---------|
| `filename` None | Dùng `"upload.bin"` |
| ingest không hỗ trợ MIME | Lỗi từ ingest module |
| session_id không khớp chat | Source vẫn gắn session_id đó |

---

### Z.2.5.14 — Route `POST /domain-rules/confirm`

**Vị trí mã:** dòng 177–182.

**Handler:** `confirm_domain_rule(body, user)`

Ủy quyền `get_orchestrator().confirm_domain_rule(rule_id, confirmed, user)`.

#### Edge

- Rule đã confirm — idempotent tùy orchestrator.

---

### Z.2.5.15 — Route `POST /feedback`

**Vị trí mã:** dòng 185–205.

**Handler:** `def feedback(body: FeedbackRequest, user) -> dict[str, str]`

#### Luồng chi tiết

1. Nếu `orch.feedback` truthy (Mongo indexer):
   - Tạo `FeedbackRecord` với `actor_id=user["sub"]`, `source="explicit"`, `confidence=1.0`.
   - `orch.feedback.on_user_feedback(record)`.
2. Nếu `sentiment == "positive"` và có `analysis_tool_registry`:
   - `find_by_trace(trace_id)` → nếu có tool → `promote(tool_id)`.
3. Luôn trả `{"status": "ok"}` — kể cả không có Mongo feedback.

#### Người gọi

- UI nút thumbs up/down sau phân tích.

#### Edge

| Tình huống | Hành vi |
|------------|---------|
| Mongo None | Bỏ qua ghi — vẫn 200 ok |
| sentiment positive nhưng không có tool | Không promote |
| trace_id không tồn tại | promote không chạy |

---

### Z.2.5.16 — Route `GET /analysis/{analysis_id}/status`

**Vị trí mã:** dòng 208–210.

**Handler:** `analysis_status(analysis_id, user)`

**Path param:** `analysis_id`.

**Đầu ra:** Dict trạng thái từ orchestrator — pending/running/done/error.

**Edge:** `user` inject nhưng handler không truyền `user` vào `analysis_status` — authorization theo analysis_id only tại orchestrator.

---

### Z.2.5.17 — Route `GET /artifacts/{trace_id}/{file_name}`

**Vị trí mã:** dòng 213–228.

**Handler:** `get_artifact(trace_id, file_name, session_id=None, user)`

#### Bảo mật path (dòng 220–221)

Từ chối `file_name` chứa `..`, `/`, `\` → HTTP 400 `invalid_path`.

#### Resolve file (dòng 222–225)

`base = Path(ARTIFACTS_DIR or "data/artifacts") / trace_id / "out"`.

Không tồn tại → 404 `not_found`.

#### Download tracking (dòng 226–227)

Nếu query `session_id` có → `record_artifact_download(session_id, trace_id)`.

#### Đầu ra

`FileResponse(path)` — stream file.

#### Edge

| Tình huống | Rủi ro |
|------------|--------|
| Biết trace_id UUID | Có thể tải nếu auth JWT hợp lệ — không check ownership sâu tại app |
| Symlink trong out_dir | FileResponse follow — cần sandbox filesystem |
| session_id thiếu | Vẫn trả file — không ghi analytics download |

---

### Z.2.5.18 — Hàm `main() -> None`

**Vị trí mã:** dòng 231–234.

**Mục đích:** Entry point CLI `python -m chat_gateway.app`.

**Hành vi:** `uvicorn.run("chat_gateway.app:app", host="0.0.0.0", port=CHAT_GATEWAY_PORT or 18300)`.

#### Người gọi

`if __name__ == "__main__": main()`.

#### Edge

- Port trùng — OSError bind.

## §Z.2.6 — `agents/chat-gateway/src/chat_gateway/clients.py`

**Vai trò:** HTTP client adapters — `HttpAgentInvoker` gọi 4 agent `/run`, `HttpSqlGatewayClient` gọi sql-gateway `/tools/*`. Cả hai tích hợp circuit breaker và internal auth headers.

**Logger:** `logger = logging.getLogger(__name__)` — cảnh báo 404 sql-gateway.

---

### Z.2.6.1 — Lớp `HttpAgentInvoker`

**Kế thừa:** `AgentInvoker` từ `project_core.domain.budget` — interface pipeline dùng để gọi agent I–IV.

---

#### Z.2.6.1.1 — `__init__(self, *, client, circuit, trace_id, analysis_id)`

**Vị trí mã:** dòng 20–38.

##### Tham số keyword-only

| Tham số | Mặc định | Mô tả |
|---------|----------|-------|
| `client` | `None` | `httpx.Client` dùng chung — orchestrator inject để pool connection |
| `circuit` | `None` → `CircuitBreaker()` | Cắt request khi agent lỗi liên tiếp |
| `trace_id` | `None` | Header `X-Trace-Id` |
| `analysis_id` | `None` | Header `X-Analysis-Id` |

##### Side effect: `self.urls`

Dict cố định keys `"I"`, `"II"`, `"III"`, `"IV"`:

| Key | Env | Default URL |
|-----|-----|-------------|
| I | `AGENT_I_URL` | `http://localhost:18201` |
| II | `AGENT_II_URL` | `http://localhost:18202` |
| III | `AGENT_III_URL` | `http://localhost:18203` |
| IV | `AGENT_IV_URL` | `http://localhost:18204` |

##### `self._owns_client`

`True` nếu không inject client — `close()` sẽ đóng client tự tạo.

##### Người gọi

- `ChatOrchestrator.__init__` — `HttpAgentInvoker(client=self._http)`.
- Nhiều method orchestrator tạo invoker mới với `set_trace` per analysis.

##### Edge

- Env URL thiếu scheme — httpx lỗi khi post.
- Key agent lạ không có trong `urls` — `KeyError` tại `invoke`.

---

#### Z.2.6.1.2 — `_get_client(self) -> httpx.Client`

**Vị trí mã:** dòng 40–43.

Lazy tạo `httpx.Client(timeout=120.0)` nếu `self._client is None`.

**Timeout 120s** — phù hợp LLM agent chậm.

**Người gọi:** `invoke` nội bộ.

**Edge:** Client đã close mà gọi lại — tạo mới nếu `_client` set None sau close.

---

#### Z.2.6.1.3 — `close(self) -> None`

**Vị trí mã:** dòng 45–48.

Đóng client chỉ khi `_owns_client` và client không None; sau đó set `_client = None`.

**Người gọi:** Orchestrator shutdown / context manager (nếu có).

**Edge:** Client inject từ ngoài — close không đóng shared pool.

---

#### Z.2.6.1.4 — `set_trace(self, *, trace_id=None, analysis_id=None) -> None`

**Vị trí mã:** dòng 50–54.

Cập nhật header cho request sau:

- Chỉ gán nếu tham số **không** `None` — không xóa trace cũ bằng `None` explicit.

**Người gọi:** Pipeline trước mỗi analysis run.

**Edge:** Muốn clear trace — phải tạo invoker mới hoặc set field trực tiếp (không API public).

---

#### Z.2.6.1.5 — `invoke(self, agent: str, payload: dict, metadata: dict) -> dict`

**Vị trí mã:** dòng 56–89.

**Đây là phương thức quan trọng nhất của chat-gateway clients** — mọi bước agent pipeline đi qua đây.

##### Đầu vào

| Tham số | Mô tả |
|---------|-------|
| `agent` | `"I"` \| `"II"` \| `"III"` \| `"IV"` |
| `payload` | Dict serializable — sẽ `json.dumps` vào `AgentRequest.message` |
| `metadata` | Dict — session_id, actor_id, mode, permissions, ... |

##### Bước 1 — Circuit breaker (dòng 57–58)

`is_open()` → raise `AgentUnavailableError(f"Circuit open for agent {agent}")`.

##### Bước 2 — Build request (dòng 59–65)

```python
url = f"{self.urls[agent]}/run"
req = AgentRequest(
    session_id=metadata.get("session_id", "system"),
    actor_id=metadata.get("actor_id", "system"),
    message=json.dumps(payload),
    metadata=metadata,
)
```

**Edge:** `json.dumps` default không `ensure_ascii=False` — ký tự Unicode trong payload escape `\uXXXX`.

##### Bước 3 — Headers (dòng 66–70)

`internal_auth_headers()` + optional `X-Trace-Id`, `X-Analysis-Id`.

##### Bước 4 — HTTP POST (dòng 71–78)

- `raise_for_status()` — 4xx/5xx → exception.
- Success: `record_success()` trên circuit.
- Any exception: `record_failure()` rồi re-raise.

##### Bước 5 — Parse response (dòng 79–89)

1. Đọc `usage_tokens` từ `data.metadata` nếu có.
2. `out = data.get("payload") or {}`.
3. Fallback: nếu `out` rỗng và có `data["content"]` → thử `json.loads(content)`; `JSONDecodeError` → `{"content": raw}`.

##### Đầu ra

`dict` — payload agent đã parse.

##### Người gọi

- `SupermarketAnalysisPipeline` mọi bước I→II→III→IV.
- Integration test với stub patch.

##### Ma trận lỗi

| Lỗi | Circuit | Caller nhận |
|-----|---------|---------------|
| Connection refused | failure++ | AgentUnavailableError sau đủ lần |
| HTTP 500 | failure++ | httpx HTTPStatusError |
| JSON response không có payload/content | — | `{}` rỗng — pipeline có thể break |
| Agent trả HTML error page | JSONDecodeError path | `{"content": "<html>..."}` |

---

### Z.2.6.2 — Lớp `HttpSqlGatewayClient`

**Kế thừa:** `SqlGatewayClient` — interface validate/explain/execute SQL.

---

#### Z.2.6.2.1 — `__init__(self, *, client, circuit, trace_id)`

**Vị trí mã:** dòng 93–104.

| Field | Giá trị |
|-------|---------|
| `self.base` | `SQL_GATEWAY_URL` hoặc `http://localhost:18101` |
| timeout client | 60s (ngắn hơn agent) |
| `trace_id` | Chỉ trace, không analysis_id |

**Người gọi:** Orchestrator cùng shared `httpx.Client` với invoker.

---

#### Z.2.6.2.2 — `_get_client` / `close`

**Vị trí mã:** dòng 106–114.

Tương tự invoker với timeout 60.0.

---

#### Z.2.6.2.3 — `set_trace(self, trace_id: str | None) -> None`

**Vị trí mã:** dòng 116–117.

Chỉ một trace_id — đơn giản hơn invoker.

---

#### Z.2.6.2.4 — `_call(self, tool: str, arguments: dict) -> dict`

**Vị trí mã:** dòng 119–140.

**Mục đích:** RPC tới sql-gateway tool endpoint hoặc in-process shortcut.

##### Nhánh in-process (dòng 122–126)

Khi `SQL_GATEWAY_INPROCESS == "1"`:

```python
from sql_gateway import tools_impl as impl
fn = getattr(impl, tool)
return fn(**arguments)
```

**Edge:** `tool` không tồn tại → AttributeError. Dùng cho test local không cần HTTP server.

##### Nhánh HTTP (dòng 127–140)

POST `{base}/tools/{tool}` JSON body `arguments`.

- 404: **không** raise — log warning, return `{"error": "gateway_not_found", "status": 404}`.
- Khác: `raise_for_status()`, circuit success/failure.

##### Người gọi

- `validate_sql`, `explain_sql`, `execute_readonly` public methods.

##### Edge

| Tình huống | Hành vi |
|------------|---------|
| Circuit open | AgentUnavailableError |
| 404 gateway | Dict error — pipeline phải handle |
| Response không phải JSON | httpx/json error |

---

#### Z.2.6.2.5 — `_acl_args(self, acl: SqlAclContext) -> dict`

**Vị trí mã:** dòng 142–143.

Delegate `acl.to_gateway_args()` — chuyển allowed_tables, store_ids, v.v. sang format gateway.

**Người gọi:** Ba method public SQL.

---

#### Z.2.6.2.6 — `validate_sql(self, sql: str, acl: SqlAclContext) -> dict`

**Vị trí mã:** dòng 145–146.

Gọi `_call("validate_sql", {"sql": sql, **acl_args})`.

**Đầu ra:** Dict verdict gateway — allowed, violations.

**Người gọi:** Pipeline trước execute (có thể song song Agent III).

---

#### Z.2.6.2.7 — `explain_sql(self, sql, acl, *, target_db="db2") -> dict`

**Vị trí mã:** dòng 148–152.

Thêm `target_db` vào arguments — chọn connection db1/db2.

**Edge:** `target_db` sai — lỗi từ gateway connection pool.

---

#### Z.2.6.2.8 — `execute_readonly(self, sql, acl, *, target_db="db2") -> dict`

**Vị trí mã:** dòng 154–158.

Thực thi SELECT readonly — trả parquet path, row count, columns.

**Người gọi:** Pipeline sau III approve.

**Edge:** Query quá lớn — timeout 60s client có thể cắt trước gateway hoàn tất.

---

## §Z.2.7 — `agents/chat-gateway/src/chat_gateway/auth.py`

**Vai trò:** JWT bearer authentication — phát hành token, decode, FastAPI dependency `current_user`.

**Module-level side effect:** `_validate_jwt_secret_at_startup()` chạy khi import (dòng 29).

---

### Z.2.7.1 — Hằng số và cấu hình

| Tên | Giá trị | Mô tả |
|-----|---------|-------|
| `_bearer` | `HTTPBearer(auto_error=False)` | Không auto 403 khi thiếu header |
| `JWT_SECRET` | env hoặc `"change-me-in-production"` | Khóa ký HS256 |
| `JWT_ALG` | `"HS256"` | Thuật toán |
| `_WEAK_SECRETS` | frozenset weak strings | Kiểm tra production |

---

### Z.2.7.2 — Hàm `_validate_jwt_secret_at_startup() -> None`

**Vị trí mã:** dòng 21–26.

#### Logic

- Nếu `REQUIRE_PROD_AUTH=1`:
  - Secret rỗng, trong weak set, hoặc `len < 32` → `RuntimeError` crash process.
- Else nếu secret weak → `logger.warning` — cho phép dev tiếp tục.

#### Người gọi

Import module lúc startup uvicorn.

#### Edge

- Đổi `JWT_SECRET` runtime không re-validate — chỉ lúc import.
- `REQUIRE_PROD_AUTH` unset trong prod — chỉ warning, không crash.

---

### Z.2.7.3 — Hàm `issue_token(actor_id, role, store_ids=None) -> str`

**Vị trí mã:** dòng 32–40.

#### Đầu vào

| Tham số | Kiểu | Mô tả |
|---------|------|-------|
| `actor_id` | `str` | Claim `sub` — user_id |
| `role` | `str` | Vai trò RBAC |
| `store_ids` | `list[int] \| None` | Cửa hàng được phép — normalize qua `normalize_store_ids` |

#### Payload JWT

```python
{
  "sub": actor_id,
  "role": role,
  "store_ids": normalized_stores,
  "exp": utc_now() + timedelta(hours=8),
}
```

#### Đầu ra

Chuỗi JWT encoded `jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)`.

#### Người gọi

- `app.dev_login`, `app.login`.
- `oauth.py` sau exchange code.

#### Edge

| Tình huống | Hành vi |
|------------|---------|
| `store_ids` rỗng `[]` | normalize → có thể `[]` hoặc `None` tùy helper |
| Token không có `iat` | Chỉ exp — client không biết thời điểm phát hành |
| Clock skew | exp strict server-side decode |

---

### Z.2.7.4 — Hàm `decode_token(token: str) -> dict`

**Vị trí mã:** dòng 43–47.

#### Đầu vào

Raw JWT string (không có prefix `Bearer`).

#### Đầu ra

Dict claims decoded.

#### Lỗi

`jwt.PyJWTError` → wrap `HTTPException(401, detail="invalid_token")`.

#### Người gọi

- `current_user` dependency.

#### Edge

- Token hết hạn — PyJWTError subclass ExpiredSignatureError.
- Sai secret — invalid signature.
- Algorithm none attack — chỉ cho phép `algorithms=[JWT_ALG]`.

---

### Z.2.7.5 — Coroutine `current_user(credentials = Depends(_bearer)) -> dict`

**Vị trí mã:** dòng 50–59.

**FastAPI dependency** — inject vào mọi route bảo vệ.

#### Nhánh không có credentials (dòng 53–56)

- `ALLOW_DEV_AUTH=1` → return hardcoded `{"sub": "dev-user", "role": "hq_analyst", "store_ids": None}`.
- Ngược lại → HTTP 401 `missing_token`.

#### Nhánh có credentials (dòng 57–59)

1. `decode_token(credentials.credentials)`.
2. `claims["store_ids"] = normalize_store_ids(claims.get("store_ids"))`.
3. Return claims dict.

#### Người gọi

FastAPI Depends trên: `/chat`, `/chat/clarify`, `/attachments`, `/domain-rules/confirm`, `/feedback`, `/analysis/.../status`, `/artifacts/...`.

#### Edge

| Tình huống | Hành vi |
|------------|---------|
| Header `Authorization: Bearer` malformed | credentials None hoặc decode fail |
| Dev auth + token invalid cùng lúc | Vẫn ưu tiên credentials nếu có |
| Role string tùy ý trong JWT | Không validate với DB tại auth layer |

---

## §Z.2.8 — `agents/chat-gateway/src/chat_gateway/auth_store.py`

**Vai trò:** Truy cập SQL Server AUTH database — đăng nhập password, load permissions RBAC, cache TTL.

**Dependencies:** `pyodbc`, `bcrypt`, `PermissionSet`, `normalize_store_ids`.

---

### Z.2.8.1 — Cache permissions module-level

| Biến | Mô tả |
|------|-------|
| `_perm_cache` | `dict[user_id, (expiry_monotonic, PermissionSet)]` |
| `_PERM_CACHE_TTL` | Giây, env `AUTH_PERMISSIONS_CACHE_TTL` default 60 |

**Edge:** Revoke permission trong DB — tối đa TTL giây mới có hiệu lực.

---

### Z.2.8.2 — Dataclass `AuthUser`

**Vị trí mã:** dòng 21–28.

| Field | Kiểu | Mô tả |
|-------|------|-------|
| `user_id` | `str` | PK users |
| `username` | `str` | Login name |
| `role` | `str` | role_key RBAC |
| `store_ids` | `list[int] \| None` | Phạm vi cửa hàng |
| `display_name` | `str` | Hiển thị UI |
| `email` | `str` | Email |

`frozen=True` — immutable sau tạo.

---

### Z.2.8.3 — Hàm `_connect() -> pyodbc.Connection`

**Vị trí mã:** dòng 31–35.

#### Logic

1. Đọc `AUTH_DB_DSN` strip whitespace.
2. Rỗng → `RuntimeError("AUTH_DB_DSN not configured")`.
3. `pyodbc.connect(dsn, timeout=15)`.

#### Người gọi

`authenticate`, `load_effective_permissions`, `get_user_by_id`.

#### Edge

| Tình huống | Hành vi |
|------------|---------|
| DSN sai | pyodbc.Error — caller catch |
| Pool exhaustion | Timeout 15s |
| Windows vs Linux driver | Phụ thuộc ODBC driver trong DSN |

---

### Z.2.8.4 — Hàm `verify_password(password, password_hash) -> bool`

**Vị trí mã:** dòng 38–44.

#### Đầu vào

- `password` plain UTF-8.
- `password_hash` bcrypt string từ DB.

#### Logic

- Hash rỗng → `False`.
- `bcrypt.checkpw` — `ValueError` (hash malformed) → `False`.

#### Người gọi

`authenticate`.

#### Edge

- Password > 72 bytes bcrypt limit — bcrypt cắt hoặc lỗi tùy version.
- Timing: checkpw designed constant-time vs hash.

---

### Z.2.8.5 — Hàm `hash_password(password: str) -> str`

**Vị trí mã:** dòng 47–48.

`bcrypt.gensalt(rounds=12)` — dùng seed script, không gọi từ app login path.

**Người gọi:** `scripts/seed_auth.py` (ngoài module này).

---

### Z.2.8.6 — Hàm `_row_to_user(row) -> AuthUser`

**Vị trí mã:** dòng 51–60.

Chuyển pyodbc row — hỗ trợ **cả** named columns (`row.user_id`) và index (`row[0]`).

**Cột thứ tự index:** 0=user_id, 1=username, 2=role, 3=password_hash (bỏ qua trong output), 4=store_ids, 5=display_name, 6=email.

`store_ids` qua `normalize_store_ids`.

#### Edge

- Row thiếu cột — IndexError.
- `store_ids` JSON string trong DB — normalize parse.

---

### Z.2.8.7 — Hàm `authenticate(username, password) -> AuthUser | None`

**Vị trí mã:** dòng 63–91.

**Docstring:** Lookup user by username and verify bcrypt password_hash.

#### Luồng

1. `username.strip()` — password không strip.
2. Rỗng username hoặc password → `None`.
3. SQL:
   ```sql
   SELECT user_id, username, role, password_hash, store_ids, display_name, email
   FROM users WHERE username = ? AND is_active = 1
   ```
4. Không row → `None`.
5. Verify password — fail → `None`.
6. `_row_to_user(row)`.

#### Exception handling

- `pyodbc.Error` → log warning, `None`.
- `RuntimeError` (DSN missing) → log warning, `None`.

**Không phân biệt** user không tồn tại vs sai password — luôn `None` → app trả 401 chung.

#### Người gọi

- `app.login` POST `/auth/login`.

#### Edge

| Tình huống | Hành vi |
|------------|---------|
| SQL injection | Parameterized `?` — an toàn |
| Username case sensitivity | Phụ thuộc collation SQL Server |
| is_active=0 | Như user không tồn tại |
| DB chậm | Block tới 15s connect + query |

---

### Z.2.8.8 — Hàm `load_effective_permissions(user_id: str) -> PermissionSet | None`

**Vị trí mã:** dòng 94–142.

**Docstring mô tả:** role_permissions UNION user grant MINUS user revoke.

#### Cache (dòng 105–108)

Hit cache nếu `cached[0] > time.monotonic()` → return `PermissionSet` ngay.

#### DB flow

1. SELECT role FROM users WHERE user_id=? AND is_active=1 — không row → `None`.
2. SELECT permission_key FROM role_permissions WHERE role_key=? → set `keys`.
3. SELECT permission_key, effect FROM user_permissions WHERE user_id=?:
   - effect `revoke` (case insensitive) → `keys.discard(pk)`.
   - else → `keys.add(pk)`.
4. `PermissionSet.from_keys(keys)` — cache với expiry `now + TTL`.

#### Đầu ra

- `PermissionSet` — capabilities cho ContextPolicy.
- `None` — user inactive, DB lỗi, DSN thiếu.

#### Người gọi

- `ChatOrchestrator` / pipeline khi build `PermissionsSnapshot` cho agent payload.

#### Fail-closed semantics

Docstring: callers treat `None` as deny — chỉ `ALLOW_DEV_AUTH` fallback YAML roles.

#### Edge

| Tình huống | Hành vi |
|------------|---------|
| Permission key lạ trong DB | Vẫn vào set — ContextPolicy quyết định ý nghĩa |
| Nhiều revoke cùng key | Idempotent discard |
| User đổi role | Cache stale tới TTL |
| Empty permission set | `PermissionSet` rỗng — valid, deny hầu hết tools |

---

### Z.2.8.9 — Hàm `get_user_by_id(user_id: str) -> AuthUser | None`

**Vị trí mã:** dòng 145–163.

SELECT cùng cột như authenticate nhưng filter `user_id = ?`.

**Không** verify password — dùng refresh profile, admin lookup.

#### Exception

`except Exception` broad — log warning, `None`.

#### Người gọi

- Có thể orchestrator/oauth — không qua app.py trực tiếp trong file đã đọc.

#### Edge

- Trả về cả password_hash trong row nhưng `_row_to_user` không expose hash — OK.
- user_id không phải username — UUID/string PK.

---

## §Z.2.9 — Bảng tổng hợp luồng gọi chéo các tệp

| Bước người dùng | app.py | auth.py | auth_store.py | clients.py | Agent service |
|-----------------|--------|---------|---------------|------------|---------------|
| Login password | `login` | `issue_token` | `authenticate` | — | — |
| Chat message | `chat` | `current_user` | `load_effective_permissions`* | `invoke("I")` | `ConversationalRouterService.decide` |
| Pipeline SQL | — | — | — | `invoke("II")`, `validate_sql` | `SqlPlannerService.decide` |
| Review SQL | — | — | — | `invoke("III")` | `RiskReviewerService.decide` |
| Analyze | — | — | — | `invoke("IV")` | `DataAnalystService.decide` |

\*Permissions load tại orchestrator, không trực tiếp trong app.py.

---

## §Z.2.10 — Biến môi trường liên quan trực tiếp các tệp §Z.2

| Biến | Tệp sử dụng | Tác dụng |
|------|-------------|----------|
| `ALLOW_LLM_STUB` | service.py agents I–III | Stub không OpenRouter |
| `ALLOW_DEV_AUTH` | auth.py, app dev_login | Bypass JWT / dev user |
| `REQUIRE_PROD_AUTH` | auth.py | Ép JWT_SECRET mạnh |
| `JWT_SECRET` | auth.py | Ký token |
| `AGENT_I_URL` … `AGENT_IV_URL` | clients.py | Base URL agents |
| `SQL_GATEWAY_URL` | clients.py | Base URL gateway |
| `SQL_GATEWAY_INPROCESS` | clients.py | Gọi tools_impl local |
| `AUTH_DB_DSN` | auth_store.py | ODBC AUTH database |
| `AUTH_PERMISSIONS_CACHE_TTL` | auth_store.py | Cache permissions |
| `CHAT_GATEWAY_PORT` | app.py main | Port uvicorn |
| `ARTIFACTS_DIR` | app.py get_artifact | Thư mục artifact |

---

## §Z.2.11 — Kết luận phần Z.2

Phần Z.2 đã mô tả **toàn bộ** hàm và phương thức public/private trong 8 tệp mã nguồn được chỉ định, với đầu vào, đầu ra, chuỗi gọi, và trường hợp biên riêng cho từng symbol. Các tệp này tạo thành **xương sống runtime** của stack supermarket: JWT auth → orchestrator → HTTP invoker → agent decide → sql gateway → iv analyzer.

*Hết §Z.2 — chi tiết service agents và chat-gateway.*

---

## §Z.2.6 — `packages/project-core/src/project_core/orchestration/pipeline.py`

**Vai trò:** `SupermarketAnalysisPipeline` — lõi điều phối đồng bộ chuỗi II→III→SQL→IV; trả `PipelineResult`. Không HTTP/Redis.

**Số dòng:** 696. **Người gọi:** `ChatOrchestrator._run_pipeline_and_respond`.

### §Z.2.6.0 — Import dòng 1–44 (chi tiết từng dòng)

**Dòng 1 `from __future__ import annotations`:** Hoãn resolve type hints; hỗ trợ `X | Y` và forward reference không cần quote.

**Dòng 3 `import json`:** Chuẩn JSON; không gọi trực tiếp trong file — serialization qua Pydantic `model_dump`.

**Dòng 4 `import time`:** `time.monotonic()` cho `sync_deadline` và `_deadline_exceeded` — đồng hồ không bị NTP chỉnh lùi.

**Dòng 5 `Callable`:** Type hint callback `on_progress: Callable[[WorkflowState], None] | None`.

**Dòng 6 `Path`:** Tạo `artifact_base/trace_id/raw|out`, ghi parquet, ghép URL artifact.

**Dòng 7 `Any`:** Kiểu inject lỏng cho feedback_loop, registry, domain_rule_store; `inbox: dict[str, Any]`.

**Dòng 8 `uuid4`:** `trace_id` mỗi `run()`; `step_id` mỗi `WorkflowStep`.

**Dòng 10 `pandas`:** `DataFrame(rows)` → parquet; `columns`, `len(df)` cho manifest.

**Dòng 12 `load_project_config`:** Đọc YAML — `max_sql_retries`, `max_clarify_rounds`, `artifacts.base_dir`, v.v.

**Dòng 13 `ContextPolicy`:** `filter_schema_excerpt`, `can_invoke_tool`, `can_execute_sql`, `can_invoke_function`.

**Dòng 14 `decompose_brief`:** Tạo `brief.plan` nếu None trước vòng SQL.

**Dòng 15 `build_execution_plan`:** Ghép plan + parquet paths → `execution_steps` cho IV.

**Dòng 16 `rank_candidates`:** Fallback rank recipe khi không có Mongo registry.

**Dòng 17 `AuditLogger`:** `log_sql_explain`, `log_sql_execute`.

**Dòng 18 `apply_data_feedback`:** Merge IV feedback vào brief đầu mỗi sql_attempt.

**Dòng 19:** `AnalystResponse`, `RiskReviewResponse`, `SqlPlannerResponse` — output contract II/III/IV.

**Dòng 20–21:** `AnalysisBrief`, `TechnicalSummary`, `ClarificationRequest`.

**Dòng 22 `DataFeedback`:** Validate feedback IV; diagnosis, probe_requests, confirmed_rules.

**Dòng 23 `parse_agent_response`:** Raw dict → typed model; `ContractInvalidError`.

**Dòng 24–29:** `ExtractedDataset`, `PipelineResult`, `QueryResultFile`, `ResultProfile`.

**Dòng 30 `SqlAclContext`:** `from_permissions` cho gateway explain/execute.

**Dòng 31 `build_result_profile`:** Profile một DataFrame; merge qua `_merge_profiles`.

**Dòng 32–39:** Workflow contracts — `AnalysisOutcome`, `PermissionsSnapshot`, `WorkflowState`, `WorkflowStep`, `WorkflowStepType`.

**Dòng 40:** `ClarifyRoundsExceededError`, `ContractInvalidError`.

**Dòng 41–44:** `AgentInvoker`, `SqlGatewayClient`, `SupermarketBudgetGuard`, `TraceBudget`, `PolicyEngine`, `suggest_query_plan`, `SchemaCatalog`.

### §Z.2.6.1 — Lớp `SupermarketAnalysisPipeline` (dòng 47)

Class composition-only; public: `__init__`, `run`; private: `_deadline_exceeded`, `_emit_progress`, `_finish`, `_merge_profiles`; module: `_needs_explain_from_feedback`.

### §Z.2.6.2 — `__init__` (dòng 48–67)

Keyword-only sau `*`. Bắt buộc: `agent_invoker`, `sql_gateway`. Tùy chọn: `catalog` (default `from_dictionary_dir()`), `feedback_loop`, `analysis_tool_registry`, `domain_rule_store`, `audit_logger` (default `AuditLogger()`). Gán `self.cfg = load_project_config()`, `self.context_policy = ContextPolicy()`. Không gọi agent/SQL tại init.

### §Z.2.6.3 — `run()` chữ ký (dòng 69–78)

Tham số keyword-only: `brief`, `workflow`, `permissions`; tùy chọn `trace_budget`, `on_progress`, `deadline`. Trả `PipelineResult`. Có thể `raise ClarifyRoundsExceededError` (orchestrator bắt).

### §Z.2.6.4 — Khối trace/deadline (dòng 79–88)

`trace_id = str(uuid4())`. `analysis_id = workflow.active_analysis_id or trace_id`. `sync_deadline` từ `deadline` hoặc `monotonic() + max_sync_seconds`. `acl = SqlAclContext.from_permissions(permissions)`. Duck `set_trace` trên invoker/gateway. `workflow.status = RUNNING`, `sql_attempt = 1`.

### §Z.2.6.5 — Budget và artifact (dòng 91–96)

`SupermarketBudgetGuard(trace_budget or TraceBudget())`. `artifact_base = Path(cfg.artifacts.base_dir) / trace_id`. `raw_dir`, `out_dir` mkdir parents=True.

### §Z.2.6.6 — PolicyEngine (dòng 98–104)

`PolicyEngine(catalog, allowed_tables, denied_columns, store_ids, store_filter_required)` — validate từng SQL trong vòng lặp.

### §Z.2.6.7 — Inbox, domain, plan (dòng 106–117)

`inbox = {}`. `needs_clarification = None`. `domain_excerpt` từ `domain_rule_store.excerpt_for_agents()` nếu có. `decompose_brief` nếu `brief.plan is None`. `promoted_tools = registry.find_promoted()` nếu có registry.

### §Z.2.6.8 — Vòng `for sql_attempt` (dòng 119–132)

`range(1, max_sql_retries + 1)`. Đầu vòng: deadline check → ERROR `sync_deadline_exceeded`. `workflow.sql_attempt = sql_attempt`. `apply_data_feedback` nếu inbox có data_feedback.

### §Z.2.6.9 — schema_context (dòng 134–147)

`budget.record("II")`. `agent_schema_bundle(allowed_tables)`. `suggest_query_plan` → key `shard_plan`. `filter_schema_excerpt` → `filtered_table_snapshot`. `domain_rules_excerpt`. `feedback_loop.retrieve_context("II", intent, actor_id)` nếu có.

### §Z.2.6.10 — Invoke agent II (dòng 149–163)

`progress_step = PLAN_SQL`, `_emit_progress`. Payload: brief, inbox, attempt, schema_context, retrieval_context (text hóa), permissions JSON. Metadata `mode: plan_sql`.

### §Z.2.6.11 — Parse II (dòng 164–180)

`parse_agent_response("II", ...)`. `ContractInvalidError` → ERROR finish. Không `SqlPlannerResponse` → `invalid_agent_ii`. `action = ii_parsed.action`.

### §Z.2.6.12 — Nhánh clarify II (dòng 182–209)

Khi `action == "clarify"` và `not exploration_mode`: `clarify_round += 1`, append CLARIFY step. Vượt `max_clarify_rounds`: unknown knowledge → exploration_mode; else raise `ClarifyRoundsExceededError`. Chưa vượt: validate `ClarificationRequest`, status AWAITING_CLARIFICATION, return NEEDS_CLARIFICATION.

### §Z.2.6.13 — Nhánh impossible II (dòng 211–220)

`_finish` IMPOSSIBLE, caveats từ `ii_parsed.reason`.

### §Z.2.6.14 — Lọc plan_sql/probe_sql (dòng 222–235)

Action khác → `continue`. Trích sql_queries, query_meta, target_dbs, default_db db2. `max_queries` cap 3 nếu probe_sql.

### §Z.2.6.15 — Vòng từng SQL `for idx, sql` — policy (dòng 237–255)

`tdb` từ target_dbs hoặc default. `policy.validate(sql)`. Không allowed: POLICY_REJECT step, inbox policy_feedback, continue.

### §Z.2.6.16 — Vòng risk III (dòng 257–337)

`sanitized = verdict.sanitized_sql or sql`. Loop `risk_attempt` 1..max_risk_retries: `budget.record("III")`, invoke III mode review, parse RiskReviewResponse. Approve → break. Else risk_feedback; nếu cần explain và `can_invoke_tool(III, explain_sql)`: explain_sql + audit; không quyền → POLICY_BLOCKED. Không approved sau loop: RISK_REJECT step, continue query.

### §Z.2.6.17 — Quyền execute và EXECUTE (dòng 339–422)

Kiểm `can_invoke_tool(II, validate_sql)` và `can_execute_sql`. progress EXECUTE. `execute_readonly`. policy_blocked gateway → audit + POLICY_REJECT continue. OK: DataFrame, parquet raw_dir, build_result_profile, QueryResultFile, approved_sql, EXECUTE step.

### §Z.2.6.18 — Không query_files (dòng 424–432)

Hết retry → POLICY_BLOCKED finish. Else continue sql_attempt.

### §Z.2.6.19 — Dataset và chuẩn bị IV (dòng 434–467)

`ExtractedDataset`, `_merge_profiles`. `budget.record("IV")`, progress SANDBOX. Recipe candidates per subtask: registry hoặc rank_candidates, lọc `_function_allowed`. `build_execution_plan` → execution_steps.

**Hàm lồng `_function_allowed(tool_id)`:** Recipe không tool_id pass; có tool_id cần `can_invoke_function`.

### §Z.2.6.20 — Invoke IV (dòng 469–503)

Payload analyze: brief, dataset_manifest, result_profile, query_meta, out_dir, max_steps, analysis_tools, recipe_candidates, analysis_plan, execution_plan, domain_rules, permissions. Parse AnalystResponse; lỗi → ERROR; `iv_action = iv_parsed.action`.

### §Z.2.6.21 — IV data_feedback (dòng 505–555)

inbox data_feedback; validate DataFeedback hoặc fallback invalid. DATA_FEEDBACK step. diagnosis impossible → IMPOSSIBLE. suggest_clarify → NEEDS_CLARIFICATION. needs_probe → probe_mode. confirmed_rules → stage_candidate. continue sql_attempt.

### §Z.2.6.22 — IV suggest_clarify / impossible (dòng 557–579)

suggest_clarify: return clarify. impossible: finish với explanation_vi, impossible_reason.

### §Z.2.6.23 — IV complete/partial (dòng 581–642)

SANDBOX step nếu sandbox_steps. progress SYNTHESIZE. SUCCESS/PARTIAL TechnicalSummary. Registry stage_step/stage_from_run. feedback_loop.on_pipeline_complete. `_finish`.

### §Z.2.6.24 — Pipeline exhausted (dòng 644–649)

Sau hết vòng sql_attempt: ERROR caveat `pipeline exhausted`.

### §Z.2.6.25 — `_deadline_exceeded` (dòng 651–653)

Static: `deadline is not None and monotonic() > deadline`.

### §Z.2.6.26 — `_emit_progress` (dòng 655–658)

Gọi `on_progress(workflow)` nếu không None.

### §Z.2.6.27 — `_finish` (dòng 660–677)

status IDLE, last_outcome, last_completed_trace_id, progress_step None. Return PipelineResult không needs_clarification.

### §Z.2.6.28 — `_merge_profiles` (dòng 679–686)

Rỗng → ResultProfile(). total_rows sum; flag empty nếu 0; columns từ profile đầu.

### §Z.2.6.29 — `_needs_explain_from_feedback` (dòng 690–694)

Module function: False nếu không dict; issue lowercase chứa performance/scan/slow/full table → True.

