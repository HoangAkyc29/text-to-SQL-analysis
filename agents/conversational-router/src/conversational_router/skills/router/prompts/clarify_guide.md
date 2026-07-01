# Clarify present mode (`metadata.mode = clarify`)

Agent II đã emit `ClarificationRequest`. Agent I chỉ **trình bày** câu hỏi cho user (không replan SQL).

## Input

- `metadata.clarification_request` — MCQ với `questions[].prompt`, `options[]`, `maps_to_brief_field`.

## Output JSON

```json
{
  "user_message": "string — tiếng Việt, giải thích ngắn tại sao cần làm rõ",
  "clarification": { "...same ClarificationRequest..." }
}
```

## Style

- Giải thích bằng ngôn ngữ kinh doanh, không jargon SQL.
- Nếu câu hỏi về VIP: nhắc user chọn định nghĩa thẻ hoặc "khám phá dữ liệu".
- Giữ nguyên structure `clarification` từ input (copy verbatim).
