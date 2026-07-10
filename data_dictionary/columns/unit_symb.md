---
semantic_key: unit_symb
title: Ký hiệu đơn vị tính (UNIT_SYMB)
display_names:
- UNIT_SYMB
kind: text
tables:
- ref: db1:strans
  column: UNIT_SYMB
  type: char
- ref: db2:asso_inf
  column: UNIT_SYMB
  type: char
- ref: db2:barcode
  column: UNIT_SYMB
  type: char
- ref: db2:hisrtpr
  column: UNIT_SYMB
  type: char
- ref: db2:hissppr
  column: UNIT_SYMB
  type: char
- ref: db2:sku_def
  column: UNIT_SYMB
  type: char
- ref: db2:st_order
  column: UNIT_SYMB
  type: char
- ref: db2:strans
  column: UNIT_SYMB
  type: char
- ref: db2:strans_tmp
  column: UNIT_SYMB
  type: char
- ref: db2:suspend
  column: UNIT_SYMB
  type: char
join_with: []
related_semantic_keys: []
facts:
- Ký hiệu đơn vị (GOI, HOP, KG, …)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ký hiệu đơn vị tính (UNIT_SYMB)

**Semantic key:** `unit_symb` · **Cột vật lý:** `UNIT_SYMB`

## Ý nghĩa nghiệp vụ

Ký hiệu đơn vị (GOI, HOP, KG, …). Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER); Master / danh mục (BARCODE, SKU_DEF).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `UNIT_SYMB` | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| `db2:asso_inf` | `UNIT_SYMB` | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| `db2:barcode` | `UNIT_SYMB` | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| `db2:hisrtpr` | `UNIT_SYMB` | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| `db2:hissppr` | `UNIT_SYMB` | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| `db2:sku_def` | `UNIT_SYMB` | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| `db2:st_order` | `UNIT_SYMB` | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| `db2:strans` | `UNIT_SYMB` | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| `db2:strans_tmp` | `UNIT_SYMB` | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| `db2:suspend` | `UNIT_SYMB` | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
