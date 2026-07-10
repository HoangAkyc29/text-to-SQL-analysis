---
semantic_key: sale_header_store_id
title: Cửa hàng trên header bill
display_names:
- STK_ID
kind: identifier
tables:
- ref: db1:transhdr_arc
  column: STK_ID
  type: char
- ref: db2:transhdr
  column: STK_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã cửa hàng / kho (10001, 10004, 10005, …)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cửa hàng trên header bill

**Semantic key:** `sale_header_store_id` · **Cột vật lý:** `STK_ID`

## Ý nghĩa nghiệp vụ

Mã cửa hàng / kho (10001, 10004, 10005, …). Dùng trong POS bán lẻ (TRANSHDR, TRANSHDR_ARC).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:transhdr_arc` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:transhdr` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
