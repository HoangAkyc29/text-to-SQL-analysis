# Agent I — Tools

Agent I **không** gọi MCP trực tiếp. Output JSON được pipeline và chat-gateway xử lý.

## Pipeline handoff

| Field output | Consumer |
|--------------|----------|
| `route` | `chat-gateway` quyết định có chạy `SupermarketAnalysisPipeline` |
| `brief` | Agent II (sql-planner) |
| `clarification` | UI MCQ + `POST /chat/clarify` |
| `user_message` | Hiển thị cho user |

## Brief fields (chuẩn hóa)

| Field | Gợi ý điền |
|-------|------------|
| `intent` | Câu hỏi phân tích nguyên văn + ngữ cảnh attachment |
| `metrics` | `revenue`, `points`, `inventory`, `qty`, … |
| `dimensions` | `store`, `time`, `product`, `month`, `STK_ID`, … |
| `filters` | `card_prefix`, `loyalty_tier`, `sku`, `product_code`, `STK_ID` |
| `time_range` | `start`, `end`, `grain` (`day`/`month`/`quarter`) |
| `output_format` | `table`, `chart`, `excel` |
| `exploration_mode` | `true` khi user không chắc định nghĩa (VIP, mã hàng, …) |

## Domain hints (không query DB)

- VIP: có thể cần `filters.card_prefix` hoặc `loyalty_tier` — nếu mơ hồ → `exploration_mode: true`
- Mã hàng: user thường đưa barcode/SKU rút gọn → `filters.product_code` hoặc `sku`
- Store manager: pipeline tự inject `STK_ID` — không cần Agent I đoán role
