---
semantic_key: gift_sqty
title: gift sqty
display_names:
- GIFT_SQTY
kind: measure
tables:
- ref: db1:strans
  column: GIFT_SQTY
  type: numeric
- ref: db2:st_order
  column: GIFT_SQTY
  type: decimal
- ref: db2:strans
  column: GIFT_SQTY
  type: numeric
- ref: db2:strans_tmp
  column: GIFT_SQTY
  type: numeric
- ref: db2:suspend
  column: GIFT_SQTY
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- 'Quà tặng: GIFT_SQTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.GIFT_SQTY: top=0.000(1000)'
- 'db2:st_order.GIFT_SQTY: top=0.000(1000)'
- 'db2:strans.GIFT_SQTY: top=0.000(1000)'
- 'db2:strans_tmp.GIFT_SQTY: top=0.000(1000)'
- 'db2:suspend.GIFT_SQTY: top=0.000(1000)'
---

# gift sqty

**Semantic key:** `gift_sqty` · **Cột vật lý:** `GIFT_SQTY`

## Ý nghĩa nghiệp vụ

Cột GIFT_SQTY trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.000; db2:st_order: top 0.000; db2:strans: top 0.000; db2:strans_tmp: top 0.000; db2:suspend: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `GIFT_SQTY` | numeric | có dữ liệu |
| `db2:st_order` | `GIFT_SQTY` | decimal | có dữ liệu |
| `db2:strans` | `GIFT_SQTY` | numeric | có dữ liệu |
| `db2:strans_tmp` | `GIFT_SQTY` | numeric | có dữ liệu |
| `db2:suspend` | `GIFT_SQTY` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.GIFT_SQTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:st_order.GIFT_SQTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans.GIFT_SQTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans_tmp.GIFT_SQTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:suspend.GIFT_SQTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Quà tặng: GIFT_SQTY
