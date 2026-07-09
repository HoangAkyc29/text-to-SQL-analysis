---
semantic_key: cdisc_rate
title: cdisc rate
display_names:
- CDISC_RATE
kind: measure
tables:
- ref: db1:strans
  column: CDISC_RATE
  type: numeric
- ref: db2:st_order
  column: CDISC_RATE
  type: decimal
- ref: db2:strans
  column: CDISC_RATE
  type: numeric
- ref: db2:strans_tmp
  column: CDISC_RATE
  type: numeric
- ref: db2:suspend
  column: CDISC_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Chiết khấu coupon: CDISC_RATE'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.CDISC_RATE: top=0.00(1000)'
- 'db2:st_order.CDISC_RATE: top=0.00(1000)'
- 'db2:strans.CDISC_RATE: top=0.00(1000)'
- 'db2:strans_tmp.CDISC_RATE: top=0.00(1000)'
- 'db2:suspend.CDISC_RATE: top=0.00(1000)'
---

# cdisc rate

**Semantic key:** `cdisc_rate` · **Cột vật lý:** `CDISC_RATE`

## Ý nghĩa nghiệp vụ

Cột CDISC_RATE trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.00; db2:st_order: top 0.00; db2:strans: top 0.00; db2:strans_tmp: top 0.00; db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `CDISC_RATE` | numeric | có dữ liệu |
| `db2:st_order` | `CDISC_RATE` | decimal | có dữ liệu |
| `db2:strans` | `CDISC_RATE` | numeric | có dữ liệu |
| `db2:strans_tmp` | `CDISC_RATE` | numeric | có dữ liệu |
| `db2:suspend` | `CDISC_RATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.CDISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.CDISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.CDISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.CDISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.CDISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Chiết khấu coupon: CDISC_RATE
