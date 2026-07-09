---
semantic_key: mark_val
title: mark val
display_names:
- MARK_VAL
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: MARK_VAL
  type: numeric
- ref: db2:crdtrans
  column: MARK_VAL
  type: numeric
- ref: db2:crdtrans_tmp
  column: MARK_VAL
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Giá trị quy đổi điểm
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.MARK_VAL: top=50000(990), 0(10)'
- 'db2:crdtrans.MARK_VAL: top=50000(985), 0(15)'
- 'db2:crdtrans_tmp.MARK_VAL: top=50000(1000)'
---

# mark val

**Semantic key:** `mark_val` · **Cột vật lý:** `MARK_VAL`

## Ý nghĩa nghiệp vụ

Cột MARK_VAL trên CRDTRANS, CRDTRANS_ARC, CRDTRANS_TMP. db1:crdtrans_arc: top 0; db2:crdtrans: top 0; db2:crdtrans_tmp: top 50000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `MARK_VAL` | numeric | có dữ liệu |
| `db2:crdtrans` | `MARK_VAL` | numeric | có dữ liệu |
| `db2:crdtrans_tmp` | `MARK_VAL` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.MARK_VAL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:crdtrans.MARK_VAL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:crdtrans_tmp.MARK_VAL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `50000`×20

## Ghi chú thêm

- Giá trị quy đổi điểm
