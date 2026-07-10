---
semantic_key: stk_type
title: stk type
display_names:
- STK_TYPE
kind: text
tables:
- ref: db1:strans
  column: STK_TYPE
  type: char
- ref: db2:st_order
  column: STK_TYPE
  type: char
- ref: db2:strans
  column: STK_TYPE
  type: char
- ref: db2:strans_tmp
  column: STK_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại kho
sources:
- table_md
- column_semantic_registry
- business_prose
---

# stk type

**Semantic key:** `stk_type` · **Cột vật lý:** `STK_TYPE`

## Ý nghĩa nghiệp vụ

Loại kho. Dùng trong POS bán lẻ (STRANS, STRANS_TMP); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `STK_TYPE` | char | Loại kho |
| `db2:st_order` | `STK_TYPE` | char | Loại kho |
| `db2:strans` | `STK_TYPE` | char | Loại kho |
| `db2:strans_tmp` | `STK_TYPE` | char | Loại kho |
