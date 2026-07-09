---
semantic_key: mdadd_rate
title: mdadd rate
display_names:
- MDADD_RATE
kind: measure
tables:
- ref: db1:strans
  column: MDADD_RATE
  type: numeric
- ref: db2:st_order
  column: MDADD_RATE
  type: numeric
- ref: db2:strans
  column: MDADD_RATE
  type: numeric
- ref: db2:strans_tmp
  column: MDADD_RATE
  type: numeric
- ref: db2:suspend
  column: MDADD_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phụ thu manual: MDADD_RATE'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.MDADD_RATE: top=0.00(1000)'
- 'db2:st_order.MDADD_RATE: top=0.00(1000)'
- 'db2:strans.MDADD_RATE: top=0.00(1000)'
- 'db2:strans_tmp.MDADD_RATE: top=0.00(1000)'
- 'db2:suspend.MDADD_RATE: top=0.00(1000)'
---

# mdadd rate

**Semantic key:** `mdadd_rate` · **Cột vật lý:** `MDADD_RATE`

## Ý nghĩa nghiệp vụ

Cột MDADD_RATE trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.00; db2:st_order: top 0.00; db2:strans: top 0.00; db2:strans_tmp: top 0.00; db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `MDADD_RATE` | numeric | có dữ liệu |
| `db2:st_order` | `MDADD_RATE` | numeric | có dữ liệu |
| `db2:strans` | `MDADD_RATE` | numeric | có dữ liệu |
| `db2:strans_tmp` | `MDADD_RATE` | numeric | có dữ liệu |
| `db2:suspend` | `MDADD_RATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.MDADD_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.MDADD_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.MDADD_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.MDADD_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.MDADD_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Phụ thu manual: MDADD_RATE
