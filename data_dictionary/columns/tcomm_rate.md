---
semantic_key: tcomm_rate
title: tcomm rate
display_names:
- TCOMM_RATE
kind: measure
tables:
- ref: db1:strans
  column: TCOMM_RATE
  type: numeric
- ref: db2:st_order
  column: TCOMM_RATE
  type: numeric
- ref: db2:strans
  column: TCOMM_RATE
  type: numeric
- ref: db2:strans_tmp
  column: TCOMM_RATE
  type: numeric
- ref: db2:suspend
  column: TCOMM_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng transaction: TCOMM_RATE'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.TCOMM_RATE: top=0.00(1000)'
- 'db2:st_order.TCOMM_RATE: top=0.00(1000)'
- 'db2:strans.TCOMM_RATE: top=0.00(1000)'
- 'db2:strans_tmp.TCOMM_RATE: top=0.00(1000)'
- 'db2:suspend.TCOMM_RATE: top=0.00(1000)'
---

# tcomm rate

**Semantic key:** `tcomm_rate` · **Cột vật lý:** `TCOMM_RATE`

## Ý nghĩa nghiệp vụ

Cột TCOMM_RATE trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.00; db2:st_order: top 0.00; db2:strans: top 0.00; db2:strans_tmp: top 0.00; db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `TCOMM_RATE` | numeric | có dữ liệu |
| `db2:st_order` | `TCOMM_RATE` | numeric | có dữ liệu |
| `db2:strans` | `TCOMM_RATE` | numeric | có dữ liệu |
| `db2:strans_tmp` | `TCOMM_RATE` | numeric | có dữ liệu |
| `db2:suspend` | `TCOMM_RATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.TCOMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.TCOMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.TCOMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.TCOMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.TCOMM_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Hoa hồng transaction: TCOMM_RATE
