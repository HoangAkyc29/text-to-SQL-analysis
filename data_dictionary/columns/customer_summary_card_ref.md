---
semantic_key: customer_summary_card_ref
title: Mã thẻ khách hàng thân thiết (CARD_ID)
display_names:
- Card_ID
kind: identifier
tables:
- ref: db2:custsumm
  column: Card_ID
  type: char
join_with:
- TRANS_NUM
- CUST_ID
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã thẻ khách hàng thân thiết (CARD_ID)

**Semantic key:** `customer_summary_card_ref` · **Cột vật lý:** `Card_ID`

## Ý nghĩa nghiệp vụ

Mã thẻ khách hàng thân thiết — bảng CUSTSUMM.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:custsumm` | `Card_ID` | char | Mã thẻ khách hàng thân thiết trên bảng custsumm |

## Join

Thường join: `TRANS_NUM`, `CUST_ID`
