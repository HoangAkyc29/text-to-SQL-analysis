---
semantic_key: pack_qty
title: pack qty
display_names:
- PACK_QTY
kind: measure
tables:
- ref: db1:strans
  column: PACK_QTY
  type: numeric
- ref: db2:strans
  column: PACK_QTY
  type: numeric
- ref: db2:strans_tmp
  column: PACK_QTY
  type: numeric
- ref: db2:suspend
  column: PACK_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượng gói
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.PACK_QTY: top=0(1000)'
- 'db2:strans.PACK_QTY: top=0(1000)'
- 'db2:strans_tmp.PACK_QTY: top=0(1000)'
- 'db2:suspend.PACK_QTY: top=0(1000)'
---

# pack qty

**Semantic key:** `pack_qty` · **Cột vật lý:** `PACK_QTY`

## Ý nghĩa nghiệp vụ

Cột PACK_QTY trên STRANS, STRANS_TMP, SUSPEND. db1:strans: top 0; db2:strans: top 0; db2:strans_tmp: top 0; db2:suspend: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `PACK_QTY` | numeric | có dữ liệu |
| `db2:strans` | `PACK_QTY` | numeric | có dữ liệu |
| `db2:strans_tmp` | `PACK_QTY` | numeric | có dữ liệu |
| `db2:suspend` | `PACK_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.PACK_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:strans.PACK_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:strans_tmp.PACK_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:suspend.PACK_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Số lượng gói
