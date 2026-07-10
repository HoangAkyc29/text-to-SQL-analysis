---
semantic_key: cust_type
title: cust type
display_names:
- CUST_TYPE
kind: text
tables:
- ref: db2:inv_iss
  column: CUST_TYPE
  type: char
- ref: db2:rdiscinf
  column: CUST_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# cust type

**Semantic key:** `cust_type` · **Cột vật lý:** `CUST_TYPE`

## Ý nghĩa nghiệp vụ

Thuộc tính cust type — dùng trong Kho / mua hàng (INV_ISS).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:inv_iss` | `CUST_TYPE` | char | Thuộc tính cust type trên phiếu xuất kho |
| `db2:rdiscinf` | `CUST_TYPE` | char | Thuộc tính cust type trên rule khuyến mãi / chiết khấu |
