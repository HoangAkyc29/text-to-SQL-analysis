---
semantic_key: unitconv
title: Hệ số quy đổi đơn vị (UNITCONV)
display_names:
- UNITCONV
kind: measure
tables:
- ref: db1:strans
  column: UNITCONV
  type: numeric
- ref: db2:asso_inf
  column: UNITCONV
  type: numeric
- ref: db2:barcode
  column: UNITCONV
  type: numeric
- ref: db2:hisrtpr
  column: UNITCONV
  type: numeric
- ref: db2:hissppr
  column: UNITCONV
  type: numeric
- ref: db2:sku_def
  column: UNITCONV
  type: numeric
- ref: db2:st_order
  column: UNITCONV
  type: numeric
- ref: db2:strans
  column: UNITCONV
  type: numeric
- ref: db2:strans_tmp
  column: UNITCONV
  type: numeric
- ref: db2:suspend
  column: UNITCONV
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Hệ số quy đổi đơn vị
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Hệ số quy đổi đơn vị (UNITCONV)

**Semantic key:** `unitconv` · **Cột vật lý:** `UNITCONV`

## Ý nghĩa nghiệp vụ

Hệ số quy đổi đơn vị. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER); Master / danh mục (BARCODE, SKU_DEF).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `UNITCONV` | numeric | Hệ số quy đổi đơn vị |
| `db2:asso_inf` | `UNITCONV` | numeric | Hệ số quy đổi đơn vị |
| `db2:barcode` | `UNITCONV` | numeric | Hệ số quy đổi đơn vị |
| `db2:hisrtpr` | `UNITCONV` | numeric | Hệ số quy đổi đơn vị |
| `db2:hissppr` | `UNITCONV` | numeric | Hệ số quy đổi đơn vị |
| `db2:sku_def` | `UNITCONV` | numeric | Hệ số quy đổi đơn vị |
| `db2:st_order` | `UNITCONV` | numeric | Hệ số quy đổi đơn vị |
| `db2:strans` | `UNITCONV` | numeric | Hệ số quy đổi đơn vị |
| `db2:strans_tmp` | `UNITCONV` | numeric | Hệ số quy đổi đơn vị |
| `db2:suspend` | `UNITCONV` | numeric | Hệ số quy đổi đơn vị |
