---
semantic_key: rfn_mark
title: rfn mark
display_names:
- RFN_MARK
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: RFN_MARK
  type: numeric
- ref: db2:crdtrans
  column: RFN_MARK
  type: numeric
- ref: db2:crdtrans_tmp
  column: RFN_MARK
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoàn / refund điểm: RFN_MARK'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.RFN_MARK: top=0.00(1000)'
- 'db2:crdtrans.RFN_MARK: top=0.00(1000)'
- 'db2:crdtrans_tmp.RFN_MARK: top=0.00(1000)'
---

# rfn mark

**Semantic key:** `rfn_mark` · **Cột vật lý:** `RFN_MARK`

## Ý nghĩa nghiệp vụ

Cột RFN_MARK trên CRDTRANS, CRDTRANS_ARC, CRDTRANS_TMP. db1:crdtrans_arc: top 0.00; db2:crdtrans: top 0.00; db2:crdtrans_tmp: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `RFN_MARK` | numeric | có dữ liệu |
| `db2:crdtrans` | `RFN_MARK` | numeric | có dữ liệu |
| `db2:crdtrans_tmp` | `RFN_MARK` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.RFN_MARK`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:crdtrans.RFN_MARK`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:crdtrans_tmp.RFN_MARK`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Hoàn / refund điểm: RFN_MARK
