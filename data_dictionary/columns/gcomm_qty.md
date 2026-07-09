---
semantic_key: gcomm_qty
title: gcomm qty
display_names:
- GCOMM_QTY
kind: measure
tables:
- ref: db1:strans
  column: GCOMM_QTY
  type: numeric
- ref: db2:st_order
  column: GCOMM_QTY
  type: numeric
- ref: db2:strans
  column: GCOMM_QTY
  type: numeric
- ref: db2:strans_tmp
  column: GCOMM_QTY
  type: numeric
- ref: db2:suspend
  column: GCOMM_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng gift: GCOMM_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.GCOMM_QTY: top=0.000(1000)'
- 'db2:st_order.GCOMM_QTY: top=0.000(1000)'
- 'db2:strans.GCOMM_QTY: top=0.000(1000)'
- 'db2:strans_tmp.GCOMM_QTY: top=0.000(1000)'
- 'db2:suspend.GCOMM_QTY: top=0.000(1000)'
---

# gcomm qty

**Semantic key:** `gcomm_qty` · **Cột vật lý:** `GCOMM_QTY`

## Ý nghĩa nghiệp vụ

Cột GCOMM_QTY trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.000; db2:st_order: top 0.000; db2:strans: top 0.000; db2:strans_tmp: top 0.000; db2:suspend: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `GCOMM_QTY` | numeric | có dữ liệu |
| `db2:st_order` | `GCOMM_QTY` | numeric | có dữ liệu |
| `db2:strans` | `GCOMM_QTY` | numeric | có dữ liệu |
| `db2:strans_tmp` | `GCOMM_QTY` | numeric | có dữ liệu |
| `db2:suspend` | `GCOMM_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.GCOMM_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:st_order.GCOMM_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans.GCOMM_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans_tmp.GCOMM_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:suspend.GCOMM_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Hoa hồng gift: GCOMM_QTY
