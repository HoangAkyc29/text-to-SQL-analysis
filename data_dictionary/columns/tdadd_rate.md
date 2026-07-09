---
semantic_key: tdadd_rate
title: tdadd rate
display_names:
- TDADD_RATE
kind: measure
tables:
- ref: db1:strans
  column: TDADD_RATE
  type: numeric
- ref: db2:st_order
  column: TDADD_RATE
  type: numeric
- ref: db2:strans
  column: TDADD_RATE
  type: numeric
- ref: db2:strans_tmp
  column: TDADD_RATE
  type: numeric
- ref: db2:suspend
  column: TDADD_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phụ thu transaction: TDADD_RATE'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.TDADD_RATE: top=0.00(1000)'
- 'db2:st_order.TDADD_RATE: top=0.00(1000)'
- 'db2:strans.TDADD_RATE: top=0.00(1000)'
- 'db2:strans_tmp.TDADD_RATE: top=0.00(1000)'
- 'db2:suspend.TDADD_RATE: top=0.00(1000)'
---

# tdadd rate

**Semantic key:** `tdadd_rate` · **Cột vật lý:** `TDADD_RATE`

## Ý nghĩa nghiệp vụ

Cột TDADD_RATE trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.00; db2:st_order: top 0.00; db2:strans: top 0.00; db2:strans_tmp: top 0.00; db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `TDADD_RATE` | numeric | có dữ liệu |
| `db2:st_order` | `TDADD_RATE` | numeric | có dữ liệu |
| `db2:strans` | `TDADD_RATE` | numeric | có dữ liệu |
| `db2:strans_tmp` | `TDADD_RATE` | numeric | có dữ liệu |
| `db2:suspend` | `TDADD_RATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.TDADD_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.TDADD_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.TDADD_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.TDADD_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.TDADD_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Phụ thu transaction: TDADD_RATE
