---
semantic_key: loyalty_card_customer_id
title: Mã khách hàng nội bộ (CUST_ID)
display_names:
- CUST_ID
kind: identifier
tables:
- ref: db2:cscard
  column: CUST_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã khách hàng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã khách hàng nội bộ (CUST_ID)

**Semantic key:** `loyalty_card_customer_id` · **Cột vật lý:** `CUST_ID`

## Ý nghĩa nghiệp vụ

Mã khách hàng nội bộ — master thẻ khách hàng thân thiết.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `CUST_ID` | char | Mã khách hàng |
