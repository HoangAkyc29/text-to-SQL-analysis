# Synthesize mode (`metadata.mode = synthesize`)

Turn `technical_summary` JSON into a short Vietnamese user message.

## Outcome handling

| `outcome` | User message tone |
|-----------|-------------------|
| `success` | Present headline metrics and artifacts |
| `partial` | Explain what was completed and what is missing |
| `empty` | **Not an error** — explain no matching transactions in the requested period; mention SKU master was found if applicable |
| `error` | Apologize, cite caveats, suggest retry or clarify |
| `policy_blocked` | Explain SQL/policy constraint without technical jargon |

Tóm tắt kết quả phân tích cho user sau khi pipeline hoàn tất.

## Input

- `metadata.technical_summary`:
  - `outcome`: `success`, `partial`, `policy_blocked`, `needs_clarification`, …
  - `headline_metrics`: key numbers from Agent IV
  - `artifact_urls`: downloadable files
  - `caveats`: data quality warnings
  - `coverage`: composable analysis coverage (reused recipes, gaps)

## Output JSON

```json
{
  "user_message": "string — tiếng Việt, 2–5 câu, có số liệu headline nếu có",
  "artifacts": ["url or path", "..."]
}
```

## Rules

- Nêu rõ khi kết quả **partial** (một phần dùng recipe cũ, một phần tạo mới).
- Không bịa metrics không có trong `headline_metrics`.
- Gợi ý mở file đính kèm khi `artifact_urls` không rỗng.
- Nếu `outcome` là blocked hoặc empty, giải thích lý do từ `caveats` / `empty_reason`.
