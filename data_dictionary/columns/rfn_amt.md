---
semantic_key: rfn_amt
title: rfn amt
display_names:
- RFN_AMT
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: RFN_AMT
  type: numeric
- ref: db2:crd_info
  column: RFN_AMT
  type: numeric
- ref: db2:crdtrans
  column: RFN_AMT
  type: numeric
- ref: db2:crdtrans_tmp
  column: RFN_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoàn / refund điểm: RFN_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.RFN_AMT: top=0.00(1000)'
- 'db2:crd_info.RFN_AMT: top=0(999), -300(1)'
- 'db2:crdtrans.RFN_AMT: top=0.00(1000)'
- 'db2:crdtrans_tmp.RFN_AMT: top=0.00(1000)'
---

# rfn amt

**Semantic key:** `rfn_amt` · **Cột vật lý:** `RFN_AMT`

## Ý nghĩa nghiệp vụ

Cột RFN_AMT trên CRDTRANS, CRDTRANS_ARC, CRDTRANS_TMP. db1:crdtrans_arc: top 0.00; db2:crd_info: top 0, -2; db2:crdtrans: top 0.00; db2:crdtrans_tmp: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `RFN_AMT` | numeric | có dữ liệu |
| `db2:crd_info` | `RFN_AMT` | numeric | có dữ liệu |
| `db2:crdtrans` | `RFN_AMT` | numeric | có dữ liệu |
| `db2:crdtrans_tmp` | `RFN_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.RFN_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:crd_info.RFN_AMT`
- Null rate trong sample: 0%
- Distinct ≈2; top: `0`×19, `-2`×1

### `db2:crdtrans.RFN_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:crdtrans_tmp.RFN_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Hoàn / refund điểm: RFN_AMT
