---
semantic_key: sale_store_id
title: Cửa hàng phát sinh dòng bán (STRANS.STK_ID)
display_names:
- STK_ID
kind: identifier
tables:
- ref: db1:strans
  column: STK_ID
  type: char
- ref: db2:strans
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

# Cửa hàng phát sinh dòng bán (STRANS.STK_ID)

**Semantic key:** `sale_store_id` · **Cột vật lý:** `STK_ID`

## Ý nghĩa nghiệp vụ

Mã cửa hàng / kho (10001, 10004, 10005, …) (ngữ cảnh: dòng bán hàng POS).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| `db2:strans` | `STK_ID` | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
