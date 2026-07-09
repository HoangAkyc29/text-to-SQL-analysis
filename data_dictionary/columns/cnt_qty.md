---
semantic_key: cnt_qty
title: cnt qty
display_names:
- CNT_QTY
kind: measure
tables:
- ref: db1:strans
  column: CNT_QTY
  type: numeric
- ref: db2:strans
  column: CNT_QTY
  type: numeric
- ref: db2:strans_tmp
  column: CNT_QTY
  type: numeric
- ref: db2:suspend
  column: CNT_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượngCNT_QTY
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.CNT_QTY: top=0.000(1000)'
- 'db2:strans.CNT_QTY: top=0.000(1000)'
- 'db2:strans_tmp.CNT_QTY: top=0.000(1000)'
- 'db2:suspend.CNT_QTY: top=0.000(1000)'
---

# cnt qty

**Semantic key:** `cnt_qty` · **Cột vật lý:** `CNT_QTY`

## Ý nghĩa nghiệp vụ

Cột CNT_QTY trên STRANS, STRANS_TMP, SUSPEND. db1:strans: top 0.000; db2:strans: top 0.000; db2:strans_tmp: top 0.000; db2:suspend: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `CNT_QTY` | numeric | có dữ liệu |
| `db2:strans` | `CNT_QTY` | numeric | có dữ liệu |
| `db2:strans_tmp` | `CNT_QTY` | numeric | có dữ liệu |
| `db2:suspend` | `CNT_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.CNT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans.CNT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans_tmp.CNT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:suspend.CNT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Số lượngCNT_QTY
