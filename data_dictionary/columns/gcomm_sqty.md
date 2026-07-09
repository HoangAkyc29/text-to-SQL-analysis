---
semantic_key: gcomm_sqty
title: gcomm sqty
display_names:
- GCOMM_SQTY
kind: measure
tables:
- ref: db1:strans
  column: GCOMM_SQTY
  type: numeric
- ref: db2:st_order
  column: GCOMM_SQTY
  type: numeric
- ref: db2:strans
  column: GCOMM_SQTY
  type: numeric
- ref: db2:strans_tmp
  column: GCOMM_SQTY
  type: numeric
- ref: db2:suspend
  column: GCOMM_SQTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Hoa hồng gift: GCOMM_SQTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.GCOMM_SQTY: top=0.000(1000)'
- 'db2:st_order.GCOMM_SQTY: top=0.000(1000)'
- 'db2:strans.GCOMM_SQTY: top=0.000(1000)'
- 'db2:strans_tmp.GCOMM_SQTY: top=0.000(1000)'
- 'db2:suspend.GCOMM_SQTY: top=0.000(1000)'
---

# gcomm sqty

**Semantic key:** `gcomm_sqty` · **Cột vật lý:** `GCOMM_SQTY`

## Ý nghĩa nghiệp vụ

Cột GCOMM_SQTY trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.000; db2:st_order: top 0.000; db2:strans: top 0.000; db2:strans_tmp: top 0.000; db2:suspend: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `GCOMM_SQTY` | numeric | có dữ liệu |
| `db2:st_order` | `GCOMM_SQTY` | numeric | có dữ liệu |
| `db2:strans` | `GCOMM_SQTY` | numeric | có dữ liệu |
| `db2:strans_tmp` | `GCOMM_SQTY` | numeric | có dữ liệu |
| `db2:suspend` | `GCOMM_SQTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.GCOMM_SQTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:st_order.GCOMM_SQTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans.GCOMM_SQTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans_tmp.GCOMM_SQTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:suspend.GCOMM_SQTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Hoa hồng gift: GCOMM_SQTY
