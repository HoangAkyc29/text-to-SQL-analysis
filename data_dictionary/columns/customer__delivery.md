---
semantic_key: customer__delivery
title: customer · delivery
display_names:
- DELIVERY
kind: flag
tables:
- ref: db2:customer
  column: DELIVERY
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột DELIVERY
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DELIVERY
- 'db2:customer.DELIVERY: top=False(1000)'
---

# customer · delivery

**Semantic key:** `customer__delivery` · **Cột vật lý:** `DELIVERY`

## Ý nghĩa nghiệp vụ

Cột DELIVERY trên CUSTOMER. db2:customer: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `DELIVERY` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:customer.DELIVERY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

