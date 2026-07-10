---
semantic_key: customer_primary_card_ref
title: Mã thẻ khách hàng thân thiết (CARD_ID)
display_names:
- CARD_ID
kind: identifier
tables:
- ref: db2:customer
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

# Mã thẻ khách hàng thân thiết (CARD_ID)

**Semantic key:** `customer_primary_card_ref` · **Cột vật lý:** `CARD_ID`

## Ý nghĩa nghiệp vụ

Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng (ngữ cảnh: danh mục master khách hàng).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `CARD_ID` | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |

## Join

Thường join: `TRANS_NUM`, `CUST_ID`
