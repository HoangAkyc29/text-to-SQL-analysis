---
semantic_key: ccomm_rate
title: ccomm rate
display_names:
- CCOMM_RATE
kind: measure
tables:
- ref: db1:strans
  column: CCOMM_RATE
  type: numeric
- ref: db2:st_order
  column: CCOMM_RATE
  type: numeric
- ref: db2:strans
  column: CCOMM_RATE
  type: numeric
- ref: db2:strans_tmp
  column: CCOMM_RATE
  type: numeric
- ref: db2:suspend
  column: CCOMM_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng coupon: CCOMM_RATE'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.CCOMM_RATE: top=0.00(1000)'
- 'db2:st_order.CCOMM_RATE: top=0.00(1000)'
- 'db2:strans.CCOMM_RATE: top=0.00(1000)'
- 'db2:strans_tmp.CCOMM_RATE: top=0.00(1000)'
- 'db2:suspend.CCOMM_RATE: top=0.00(1000)'
---

# ccomm rate

**Semantic key:** `ccomm_rate` · **Cột vật lý:** `CCOMM_RATE`

## Ý nghĩa nghiệp vụ

Cột CCOMM_RATE trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.00; db2:st_order: top 0.00; db2:strans: top 0.00; db2:strans_tmp: top 0.00; db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `CCOMM_RATE` | numeric | có dữ liệu |
| `db2:st_order` | `CCOMM_RATE` | numeric | có dữ liệu |
| `db2:strans` | `CCOMM_RATE` | numeric | có dữ liệu |
| `db2:strans_tmp` | `CCOMM_RATE` | numeric | có dữ liệu |
| `db2:suspend` | `CCOMM_RATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.CCOMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.CCOMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.CCOMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.CCOMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.CCOMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Hoa hồng coupon: CCOMM_RATE
