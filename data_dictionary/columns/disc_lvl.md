---
semantic_key: disc_lvl
title: disc lvl
display_names:
- DISC_LVL
kind: measure
tables:
- ref: db2:crd_info
  column: DISC_LVL
  type: numeric
- ref: db2:cscard
  column: DISC_LVL
  type: numeric
- ref: db2:customer
  column: DISC_LVL
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Mức chiết khấu / hạng thẻ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:crd_info.DISC_LVL: top=0(1000)'
- 'db2:cscard.DISC_LVL: top=0(790), 1(190), 2(20)'
- 'db2:customer.DISC_LVL: top=0(1000)'
---

# disc lvl

**Semantic key:** `disc_lvl` · **Cột vật lý:** `DISC_LVL`

## Ý nghĩa nghiệp vụ

Cột DISC_LVL trên CRD_INFO, CSCARD, CUSTOMER. db2:crd_info: top 0; db2:cscard: top 0; db2:customer: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `DISC_LVL` | numeric | có dữ liệu |
| `db2:cscard` | `DISC_LVL` | numeric | có dữ liệu |
| `db2:customer` | `DISC_LVL` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.DISC_LVL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:cscard.DISC_LVL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:customer.DISC_LVL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Mức chiết khấu / hạng thẻ
