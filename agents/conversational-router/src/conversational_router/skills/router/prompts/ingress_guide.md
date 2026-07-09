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
    "metrics": ["revenue"],
    "dimensions": ["store"],
    "filters": {},
    "time_range": {"start": null, "end": null, "grain": "month"},
    "output_format": ["table"],
    "exploration_mode": false,
    "user_knowledge_level": "expert",
    "external_sources": []
  },
  "satisfaction_signal": null
}
```

- `brief` is **required** when `route` is `analysis`; otherwise `null`.
- If attachments contain tabular hints (columns, sample rows in excerpt), mention them in `intent`.
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
- Map spoken bill thresholds: "600k", "600.000", "600000" → `filters.min_bill_value: 600000`.

## Examples

**User:** "So sánh doanh thu VIP tháng 5 và tháng 6 theo cửa hàng"

```json
{
  "route": "analysis",
  "user_message": "Đã nhận yêu cầu phân tích doanh thu VIP theo cửa hàng.",
  "brief": {
    "intent": "So sánh doanh thu VIP tháng 5 và tháng 6 theo cửa hàng",
    "metrics": ["revenue"],
    "dimensions": ["STK_ID"],
    "filters": {},
    "time_range": {"start": null, "end": null, "grain": "month"},
    "output_format": ["table"],
    "exploration_mode": true,
    "user_knowledge_level": "expert"
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
