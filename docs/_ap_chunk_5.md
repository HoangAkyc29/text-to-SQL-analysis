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

