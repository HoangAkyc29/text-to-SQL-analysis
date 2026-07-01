# Agent III — Risk Reviewer

Kiểm tra an toàn và chất lượng SQL từ Agent II **trước khi execute**. Kết hợp **PolicyEngine** (hard gate) và đánh giá ngữ nghĩa (LLM).

## Hard policy (luôn chạy)

- Bảng/cột nằm trong role allowlist + `data_dictionary`
- Không DML/DDL
- `TOP` / row limits
- Store filter `STK_ID` khi role `store_manager`

Nếu policy reject → `verdict: reject` (không override bằng LLM).

## Soft review (LLM khi không stub)

- Join explosion / thiếu filter thời gian
- Sai `TRANS_CODE` cho metric (vd. dùng 113 cho điểm thẻ)
- PII không cần thiết (`CARD_ID` full export)
- Cross-shard risk trên db1

## Output

```json
{
  "verdict": "approve | reject",
  "concerns": ["violation_code_or_semantic_issue"],
  "risk_feedback": {"issue": "...", "suggestion": "..."} ,
  "schema_context_summary": {"table_count": 0, "has_domain_definitions": true}
}
```

`risk_feedback` non-null khi reject — Agent II đọc qua `inbox.policy_feedback`.
