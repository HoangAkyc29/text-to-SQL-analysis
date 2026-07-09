---
semantic_key: cdisc_amt
title: cdisc amt
display_names:
- CDISC_AMT
kind: measure
tables:
- ref: db1:strans
  column: CDISC_AMT
  type: numeric
- ref: db2:st_order
  column: CDISC_AMT
  type: numeric
- ref: db2:strans
  column: CDISC_AMT
  type: numeric
- ref: db2:strans_tmp
  column: CDISC_AMT
  type: numeric
- ref: db2:suspend
  column: CDISC_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Chiết khấu coupon: CDISC_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.CDISC_AMT: top=0.00(1000)'
- 'db2:st_order.CDISC_AMT: top=0(1000)'
- 'db2:strans.CDISC_AMT: top=0.00(1000)'
- 'db2:strans_tmp.CDISC_AMT: top=0.00(1000)'
- 'db2:suspend.CDISC_AMT: top=0.00(1000)'
---

# cdisc amt

**Semantic key:** `cdisc_amt` · **Cột vật lý:** `CDISC_AMT`

## Ý nghĩa nghiệp vụ

Cột CDISC_AMT trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.00; db2:st_order: top 0; db2:strans: top 0.00; db2:strans_tmp: top 0.00; db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `CDISC_AMT` | numeric | có dữ liệu |
| `db2:st_order` | `CDISC_AMT` | numeric | có dữ liệu |
| `db2:strans` | `CDISC_AMT` | numeric | có dữ liệu |
| `db2:strans_tmp` | `CDISC_AMT` | numeric | có dữ liệu |
| `db2:suspend` | `CDISC_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.CDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.CDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:strans.CDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.CDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.CDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Chiết khấu coupon: CDISC_AMT
