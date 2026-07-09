---
semantic_key: unitconv
title: unitconv
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
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.UNITCONV: top=1(1000)'
- 'db2:asso_inf.UNITCONV: top=1(1000)'
- 'db2:barcode.UNITCONV: top=1(1000)'
- 'db2:hisrtpr.UNITCONV: top=1(1000)'
- 'db2:hissppr.UNITCONV: top=1(999), 0(1)'
- 'db2:sku_def.UNITCONV: top=1(1000)'
- 'db2:st_order.UNITCONV: top=1(1000)'
- 'db2:strans.UNITCONV: top=1(1000)'
- 'db2:strans_tmp.UNITCONV: top=1(1000)'
- 'db2:suspend.UNITCONV: top=1(1000)'
---

# unitconv

**Semantic key:** `unitconv` · **Cột vật lý:** `UNITCONV`

## Ý nghĩa nghiệp vụ

Cột UNITCONV trên ASSO_INF, BARCODE, HISRTPR. db1:strans: top 1; db2:asso_inf: top 1; db2:barcode: top 1; db2:hisrtpr: top 1; db2:hissppr: top 1; db2:sku_def: top 1; db2:st_order: top 1; db2:strans: top 1; db2:strans_tmp: top 1; db2:suspend: top 1.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `UNITCONV` | numeric | có dữ liệu |
| `db2:asso_inf` | `UNITCONV` | numeric | có dữ liệu |
| `db2:barcode` | `UNITCONV` | numeric | có dữ liệu |
| `db2:hisrtpr` | `UNITCONV` | numeric | có dữ liệu |
| `db2:hissppr` | `UNITCONV` | numeric | có dữ liệu |
| `db2:sku_def` | `UNITCONV` | numeric | có dữ liệu |
| `db2:st_order` | `UNITCONV` | numeric | có dữ liệu |
| `db2:strans` | `UNITCONV` | numeric | có dữ liệu |
| `db2:strans_tmp` | `UNITCONV` | numeric | có dữ liệu |
| `db2:suspend` | `UNITCONV` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.UNITCONV`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

### `db2:asso_inf.UNITCONV`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

### `db2:barcode.UNITCONV`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

### `db2:hisrtpr.UNITCONV`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

### `db2:hissppr.UNITCONV`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

### `db2:sku_def.UNITCONV`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

### `db2:st_order.UNITCONV`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

### `db2:strans.UNITCONV`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

### `db2:strans_tmp.UNITCONV`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

### `db2:suspend.UNITCONV`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

## Ghi chú thêm

- Hệ số quy đổi đơn vị
