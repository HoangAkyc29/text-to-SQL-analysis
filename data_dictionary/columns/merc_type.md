---
semantic_key: merc_type
title: Loại merchandise (MERC_TYPE)
display_names:
- MERC_TYPE
kind: code
tables:
- ref: db1:strans
  column: MERC_TYPE
  type: char
- ref: db2:asso_inf
  column: MERC_TYPE
  type: char
- ref: db2:plu
  column: MERC_TYPE
  type: char
- ref: db2:sku_def
  column: MERC_TYPE
  type: char
- ref: db2:strans
  column: MERC_TYPE
  type: char
- ref: db2:strans_tmp
  column: MERC_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại hàng hóa
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Loại merchandise (MERC_TYPE)

**Semantic key:** `merc_type` · **Cột vật lý:** `MERC_TYPE`

## Ý nghĩa nghiệp vụ

Loại hàng hóa. Dùng trong POS bán lẻ (STRANS, STRANS_TMP); Master / danh mục (SKU_DEF).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `MERC_TYPE` | char | Loại hàng hóa |
| `db2:asso_inf` | `MERC_TYPE` | char | Loại hàng hóa |
| `db2:plu` | `MERC_TYPE` | char | Loại hàng hóa |
| `db2:sku_def` | `MERC_TYPE` | char | Loại hàng hóa |
| `db2:strans` | `MERC_TYPE` | char | Loại hàng hóa |
| `db2:strans_tmp` | `MERC_TYPE` | char | Loại hàng hóa |
