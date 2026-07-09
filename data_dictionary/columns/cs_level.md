---
semantic_key: cs_level
title: cs level
display_names:
- CS_LEVEL
kind: measure
tables:
- ref: db2:customer
  column: CS_LEVEL
  type: numeric
- ref: db2:supplier
  column: CS_LEVEL
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột CS_LEVEL
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:customer.CS_LEVEL: top=0(1000)'
- 'db2:supplier.CS_LEVEL: top=0(1000)'
---

# cs level

**Semantic key:** `cs_level` · **Cột vật lý:** `CS_LEVEL`

## Ý nghĩa nghiệp vụ

Cột CS_LEVEL trên CUSTOMER, SUPPLIER. db2:customer: top 0; db2:supplier: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `CS_LEVEL` | numeric | có dữ liệu |
| `db2:supplier` | `CS_LEVEL` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:customer.CS_LEVEL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:supplier.CS_LEVEL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

