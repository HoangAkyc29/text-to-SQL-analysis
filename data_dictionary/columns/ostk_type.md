---
semantic_key: ostk_type
title: ostk type
display_names:
- OSTK_TYPE
kind: text
tables:
- ref: db1:strans
  column: OSTK_TYPE
  type: char
- ref: db2:st_order
  column: OSTK_TYPE
  type: char
- ref: db2:strans
  column: OSTK_TYPE
  type: char
- ref: db2:strans_tmp
  column: OSTK_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại kho đối ứng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# ostk type

**Semantic key:** `ostk_type` · **Cột vật lý:** `OSTK_TYPE`

## Ý nghĩa nghiệp vụ

Loại kho đối ứng. Dùng trong POS bán lẻ (STRANS, STRANS_TMP); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `OSTK_TYPE` | char | Loại kho đối ứng |
| `db2:st_order` | `OSTK_TYPE` | char | Loại kho đối ứng |
| `db2:strans` | `OSTK_TYPE` | char | Loại kho đối ứng |
| `db2:strans_tmp` | `OSTK_TYPE` | char | Loại kho đối ứng |
