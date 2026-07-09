---
semantic_key: rfn_rate
title: rfn rate
display_names:
- RFN_RATE
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: RFN_RATE
  type: numeric
- ref: db2:crdtrans
  column: RFN_RATE
  type: numeric
- ref: db2:crdtrans_tmp
  column: RFN_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoàn / refund điểm: RFN_RATE'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.RFN_RATE: top=0.00(1000)'
- 'db2:crdtrans.RFN_RATE: top=0.00(1000)'
- 'db2:crdtrans_tmp.RFN_RATE: top=0.00(1000)'
---

# rfn rate

**Semantic key:** `rfn_rate` · **Cột vật lý:** `RFN_RATE`

## Ý nghĩa nghiệp vụ

Cột RFN_RATE trên CRDTRANS, CRDTRANS_ARC, CRDTRANS_TMP. db1:crdtrans_arc: top 0.00; db2:crdtrans: top 0.00; db2:crdtrans_tmp: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `RFN_RATE` | numeric | có dữ liệu |
| `db2:crdtrans` | `RFN_RATE` | numeric | có dữ liệu |
| `db2:crdtrans_tmp` | `RFN_RATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.RFN_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:crdtrans.RFN_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:crdtrans_tmp.RFN_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Hoàn / refund điểm: RFN_RATE
