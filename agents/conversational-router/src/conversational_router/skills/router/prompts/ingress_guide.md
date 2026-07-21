# Ingress mode (`metadata.mode` absent or `ingress`)

## Input

- User message text (Vietnamese or English).
- Optional `external_sources[]` with `text_excerpt`, `parquet_path`, `original_name`.

## Output JSON schema

```json
{
  "route": "chitchat | analysis | confirm_cancel | wait",
  "user_message": "string — short reply to show the user",
  "brief": {
    "intent": "string",
    "metrics": ["<metric explicitly requested or optional inferred metric>"],
    "dimensions": ["<dimension explicitly requested or optional inferred dimension>"],
    "filters": {},
    "time_range": {"start": null, "end": null, "grain": "month"},
    "output_format": ["table"],
    "exploration_mode": false,
    "user_knowledge_level": "expert",
    "retrieval_facets": ["string — independent constraint sentences"],
    "external_sources": [],
    "requirements": [
      {
        "requirement_id": "metric:0",
        "kind": "metric | dimension | filter | time | ranking | output",
        "key": "canonical key",
        "source": "explicit | inferred",
        "required": true,
        "evidence_quote": "exact substring from the user message",
        "value": "value copied from the brief"
      }
    ]
  },
  "satisfaction_signal": null
}
```

- `brief` is **required** when `route` is `analysis`; otherwise `null`.
- If attachments contain tabular hints (columns, sample rows in excerpt), mention them in `intent`.
- When `route` is `analysis`, fill `retrieval_facets` (4–8 short sentences): one independent constraint each — time range, subject/filter, business attribute, metric, threshold/constraint, ranking/limit. Product codes and numeric thresholds from the user may appear in facets when they are part of the constraint.
- Emit one `requirements[]` item for every metric, dimension, filter, time constraint, ranking ask, and output format.
- Mark a requirement `source: explicit` and `required: true` only when `evidence_quote` is an exact substring of the user's message. Never make an inferred metric blocking.
- Inferred fields may remain in the brief as optional analysis context, but must use `source: inferred`, `required: false`, and an empty `evidence_quote`.
- Ranking requirements use `value: {"limit": N, "partition_by": "<dimension key>", "order_by": "<dimension key>", "direction": "asc|desc"}` with values derived only from the user's wording.
- Keywords mapping:
  - doanh thu / bán hàng / revenue → `metrics: ["revenue"]`
  - VIP / thẻ / loyalty → filters may need `card_prefix` or `loyalty_tier`; if ambiguous set `exploration_mode: true`
  - tồn kho / inventory → `metrics: ["inventory"]`
  - theo cửa hàng / store → `dimensions: ["STK_ID"]` or `["store"]`
  - biểu đồ / chart → `output_format: ["chart"]`
  - Excel → `output_format: ["excel", "table"]`
  - quà tặng / gift / mã hàng / SKU → `filters.product_code` (string or list)
  - bill / hóa đơn ≥ X / tổng bill → `filters.min_bill_value` (number); keep `min_transaction_value` as alias if user says it

## Knowledge level and exploration

- Default `user_knowledge_level: "expert"` only when the user uses technical terms (`SKU_ID`, `TRANS_NUM`, `TRANSHDR`, barcode đầy đủ).
- If user gives informal 7–8 digit product codes without technical vocabulary → `user_knowledge_level: "unknown"`, `exploration_mode: true`.
- Multiple `product_code` values + bill threshold (`min_bill_value`) without clear bill definition → `exploration_mode: true` (Agent II will clarify).
- Normalize abbreviated numeric values from the user into numbers while preserving the exact user phrase in `requirements[].evidence_quote`.

## Examples

**User:** "So sánh chỉ số A giữa hai giai đoạn theo khu vực"

```json
{
  "route": "analysis",
  "user_message": "Đã nhận yêu cầu so sánh chỉ số theo khu vực.",
  "brief": {
    "intent": "So sánh chỉ số A giữa hai giai đoạn theo khu vực",
    "metrics": ["metric_a"],
    "dimensions": ["region"],
    "filters": {},
    "time_range": {"start": null, "end": null, "grain": "month"},
    "output_format": ["table"],
    "exploration_mode": true,
    "user_knowledge_level": "expert",
    "retrieval_facets": [
      "So sánh theo hai giai đoạn",
      "Phân tích chỉ số A",
      "Chia theo khu vực"
    ],
    "requirements": [
      {
        "requirement_id": "metric:0",
        "kind": "metric",
        "key": "metric_a",
        "source": "explicit",
        "required": true,
        "evidence_quote": "chỉ số A",
        "value": "metric_a"
      },
      {
        "requirement_id": "dimension:0",
        "kind": "dimension",
        "key": "region",
        "source": "explicit",
        "required": true,
        "evidence_quote": "theo khu vực",
        "value": "region"
      }
    ]
  }
}
```

**User:** "Xin chào"

```json
{
  "route": "chitchat",
  "user_message": "Xin chào! Tôi có thể giúp bạn phân tích doanh thu, VIP, tồn kho hoặc sản phẩm. Bạn cần xem gì?",
  "brief": null
}
```
