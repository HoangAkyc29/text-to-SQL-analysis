---
semantic_key: prop_value
title: prop value
display_names:
- PROP_VALUE
kind: measure
tables:
- ref: db2:customer
  column: PROP_VALUE
  type: numeric
- ref: db2:supplier
  column: PROP_VALUE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột PROP_VALUE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:customer.PROP_VALUE: top=0.00(1000)'
- 'db2:supplier.PROP_VALUE: top=0.00(1000)'
---

# prop value

**Semantic key:** `prop_value` · **Cột vật lý:** `PROP_VALUE`

## Ý nghĩa nghiệp vụ

Cột PROP_VALUE trên CUSTOMER, SUPPLIER. db2:customer: top 0.00; db2:supplier: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `PROP_VALUE` | numeric | có dữ liệu |
| `db2:supplier` | `PROP_VALUE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:customer.PROP_VALUE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:supplier.PROP_VALUE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

