---
semantic_key: kit_qty
title: kit qty
display_names:
- KIT_QTY
kind: measure
tables:
- ref: db1:strans
  column: KIT_QTY
  type: numeric
- ref: db2:st_order
  column: KIT_QTY
  type: numeric
- ref: db2:strans
  column: KIT_QTY
  type: numeric
- ref: db2:strans_tmp
  column: KIT_QTY
  type: numeric
- ref: db2:suspend
  column: KIT_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượng kit
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.KIT_QTY: top=0.000(1000)'
- 'db2:st_order.KIT_QTY: top=0.000(1000)'
- 'db2:strans.KIT_QTY: top=0.000(999), 3.000(1)'
- 'db2:strans_tmp.KIT_QTY: top=0.000(999), 1.000(1)'
- 'db2:suspend.KIT_QTY: top=0.000(997), 1.000(2), 2.000(1)'
---

# kit qty

**Semantic key:** `kit_qty` · **Cột vật lý:** `KIT_QTY`

## Ý nghĩa nghiệp vụ

Cột KIT_QTY trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.000; db2:st_order: top 0.000; db2:strans: top 0.000; db2:strans_tmp: top 0.000; db2:suspend: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `KIT_QTY` | numeric | có dữ liệu |
| `db2:st_order` | `KIT_QTY` | numeric | có dữ liệu |
| `db2:strans` | `KIT_QTY` | numeric | có dữ liệu |
| `db2:strans_tmp` | `KIT_QTY` | numeric | có dữ liệu |
| `db2:suspend` | `KIT_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.KIT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:st_order.KIT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans.KIT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans_tmp.KIT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:suspend.KIT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Số lượng kit
