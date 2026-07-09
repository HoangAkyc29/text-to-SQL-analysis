---
semantic_key: comm_amt
title: comm amt
display_names:
- COMM_AMT
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: COMM_AMT
  type: numeric
- ref: db1:strans
  column: COMM_AMT
  type: numeric
- ref: db1:transhdr_arc
  column: COMM_AMT
  type: numeric
- ref: db2:crdtrans
  column: COMM_AMT
  type: numeric
- ref: db2:crdtrans_tmp
  column: COMM_AMT
  type: numeric
- ref: db2:custhist
  column: COMM_AMT
  type: numeric
- ref: db2:st_order
  column: COMM_AMT
  type: decimal
- ref: db2:strans
  column: COMM_AMT
  type: numeric
- ref: db2:strans_tmp
  column: COMM_AMT
  type: numeric
- ref: db2:suspend
  column: COMM_AMT
  type: numeric
- ref: db2:transhdr
  column: COMM_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tiền hoa hồng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.COMM_AMT: top=0.00(1000)'
- 'db1:strans.COMM_AMT: top=0.00(1000)'
- 'db1:transhdr_arc.COMM_AMT: top=0.00(1000)'
- 'db2:crdtrans.COMM_AMT: top=0.00(1000)'
- 'db2:crdtrans_tmp.COMM_AMT: top=0.00(1000)'
- 'db2:custhist.COMM_AMT: top=0.00(1000)'
- 'db2:st_order.COMM_AMT: top=0.00(1000)'
- 'db2:strans.COMM_AMT: top=0.00(1000)'
- 'db2:strans_tmp.COMM_AMT: top=0.00(1000)'
- 'db2:suspend.COMM_AMT: top=0.00(1000)'
- 'db2:transhdr.COMM_AMT: top=0.00(1000)'
---

# comm amt

**Semantic key:** `comm_amt` · **Cột vật lý:** `COMM_AMT`

## Ý nghĩa nghiệp vụ

Cột COMM_AMT trên CRDTRANS, CRDTRANS_ARC, CRDTRANS_TMP. db1:crdtrans_arc: top 0.00; db1:strans: top 0.00; db1:transhdr_arc: top 0.00; db2:crdtrans: top 0.00; db2:crdtrans_tmp: top 0.00; db2:custhist: top 0.00; db2:st_order: top 0.00; db2:strans: top 0.00; db2:strans_tmp: top 0.00; db2:suspend: top 0.00; db2:transhdr: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `COMM_AMT` | numeric | có dữ liệu |
| `db1:strans` | `COMM_AMT` | numeric | có dữ liệu |
| `db1:transhdr_arc` | `COMM_AMT` | numeric | có dữ liệu |
| `db2:crdtrans` | `COMM_AMT` | numeric | có dữ liệu |
| `db2:crdtrans_tmp` | `COMM_AMT` | numeric | có dữ liệu |
| `db2:custhist` | `COMM_AMT` | numeric | có dữ liệu |
| `db2:st_order` | `COMM_AMT` | decimal | có dữ liệu |
| `db2:strans` | `COMM_AMT` | numeric | có dữ liệu |
| `db2:strans_tmp` | `COMM_AMT` | numeric | có dữ liệu |
| `db2:suspend` | `COMM_AMT` | numeric | có dữ liệu |
| `db2:transhdr` | `COMM_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.COMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db1:strans.COMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db1:transhdr_arc.COMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:crdtrans.COMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:crdtrans_tmp.COMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:custhist.COMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.COMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.COMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.COMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.COMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:transhdr.COMM_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Tiền hoa hồng
