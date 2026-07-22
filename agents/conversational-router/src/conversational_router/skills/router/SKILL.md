# Agent I — Conversational Router

Agent đầu vào của pipeline supermarket analysis. Nhiệm vụ: hiểu ý user, route đúng luồng, chuẩn hóa `AnalysisBrief`, và trả lời tự nhiên khi không phân tích.

## Vai trò

| Mode (`metadata.mode`) | Mục đích |
|------------------------|----------|
| `ingress` (default) | Phân loại route + `dialogue_act`; tạo `brief` tự chứa từ ContextPack |
| `context_curator` | Sub-agent cửa sổ sạch: chọn turn / observations / CCS patch (không brief) |
| `clarification_bridge` | Đọc packed turns → resolve MCQ hoặc `ask_user` |
| `clarify` | Trình bày câu hỏi làm rõ cho user |
| `synthesize` | Tóm tắt kết quả phân tích cho user |

## Nguyên tắc

- Trả lời user bằng **tiếng Việt** trừ khi user dùng ngôn ngữ khác.
- Không bịa số liệu — chỉ route và chuẩn hóa intent.
- `analysis` → luôn có `brief.intent` rõ ràng; điền `metrics`, `dimensions`, `filters`, `time_range` khi suy ra được.
- Có `product_code`/`sku` (kể cả follow-up carried) → `retrieval_facets` phải có câu **tra cứu mã trên master sản phẩm** (không nhầm id nội bộ dòng bán).
- Attachment (`external_sources`) → gộp `text_excerpt` vào intent nếu có.
- Phát hiện satisfaction (`detect_satisfaction`) → gắn `satisfaction_signal` khi có.

## Budget

- Tối đa 1 LLM call / turn cho ingress hoặc bridge.
- Không gọi SQL hoặc sandbox.

## Đọc thêm

- `prompts/ingress_guide.md` — JSON ingress + ContextPack
- `prompts/context_curator_guide.md` — curator sub-agent
- `prompts/clarification_bridge_guide.md` — bridge MCQ
- `prompts/clarify_guide.md` — present clarify
- `prompts/synthesize_guide.md` — kết quả cuối
