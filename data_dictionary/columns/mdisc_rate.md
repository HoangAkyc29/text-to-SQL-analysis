---
semantic_key: mdisc_rate
title: mdisc rate
display_names:
- MDISC_RATE
kind: measure
tables:
- ref: db1:strans
  column: MDISC_RATE
  type: numeric
- ref: db2:st_order
  column: MDISC_RATE
  type: numeric
- ref: db2:strans
  column: MDISC_RATE
  type: numeric
- ref: db2:strans_tmp
  column: MDISC_RATE
  type: numeric
- ref: db2:suspend
  column: MDISC_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Chiết khấu manual: MDISC_RATE'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.MDISC_RATE: top=0.00(1000)'
- 'db2:st_order.MDISC_RATE: top=0.00(1000)'
- 'db2:strans.MDISC_RATE: top=0.00(1000)'
- 'db2:strans_tmp.MDISC_RATE: top=0.00(1000)'
- 'db2:suspend.MDISC_RATE: top=0.00(1000)'
---

# mdisc rate

**Semantic key:** `mdisc_rate` · **Cột vật lý:** `MDISC_RATE`

## Ý nghĩa nghiệp vụ

Cột MDISC_RATE trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.00; db2:st_order: top 0.00; db2:strans: top 0.00; db2:strans_tmp: top 0.00; db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `MDISC_RATE` | numeric | có dữ liệu |
| `db2:st_order` | `MDISC_RATE` | numeric | có dữ liệu |
| `db2:strans` | `MDISC_RATE` | numeric | có dữ liệu |
| `db2:strans_tmp` | `MDISC_RATE` | numeric | có dữ liệu |
| `db2:suspend` | `MDISC_RATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.MDISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.MDISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.MDISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.MDISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.MDISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Chiết khấu manual: MDISC_RATE
