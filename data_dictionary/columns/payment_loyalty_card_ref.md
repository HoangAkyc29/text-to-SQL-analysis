---
semantic_key: payment_loyalty_card_ref
title: Thẻ loyalty trên dòng thanh toán (PMTRANS)
display_names:
- CARD_ID
kind: identifier
tables:
- ref: db1:pmtrans
  column: CARD_ID
  type: char
- ref: db2:pmtrans
  column: CARD_ID
  type: char
join_with:
- TRANS_NUM
- CUST_ID
related_semantic_keys: []
facts:
- Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Thẻ loyalty trên dòng thanh toán (PMTRANS)

**Semantic key:** `payment_loyalty_card_ref` · **Cột vật lý:** `CARD_ID`

## Ý nghĩa nghiệp vụ

Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng (ngữ cảnh: dòng thanh toán / quỹ bill).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:pmtrans` | `CARD_ID` | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| `db2:pmtrans` | `CARD_ID` | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |

## Join

Thường join: `TRANS_NUM`, `CUST_ID`
