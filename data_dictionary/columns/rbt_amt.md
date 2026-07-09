---
semantic_key: rbt_amt
title: rbt amt
display_names:
- RBT_AMT
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: RBT_AMT
  type: numeric
- ref: db2:crdtrans
  column: RBT_AMT
  type: numeric
- ref: db2:crdtrans_tmp
  column: RBT_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Rebate: RBT_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.RBT_AMT: top=0.00(1000)'
- 'db2:crdtrans.RBT_AMT: top=0.00(1000)'
- 'db2:crdtrans_tmp.RBT_AMT: top=0.00(1000)'
---

# rbt amt

**Semantic key:** `rbt_amt` · **Cột vật lý:** `RBT_AMT`

## Ý nghĩa nghiệp vụ

Cột RBT_AMT trên CRDTRANS, CRDTRANS_ARC, CRDTRANS_TMP. db1:crdtrans_arc: top 0.00; db2:crdtrans: top 0.00; db2:crdtrans_tmp: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `RBT_AMT` | numeric | có dữ liệu |
| `db2:crdtrans` | `RBT_AMT` | numeric | có dữ liệu |
| `db2:crdtrans_tmp` | `RBT_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.RBT_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:crdtrans.RBT_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:crdtrans_tmp.RBT_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Rebate: RBT_AMT
