---
semantic_key: supplier__ord_period
title: supplier · ord period
display_names:
- ORD_PERIOD
kind: measure
tables:
- ref: db2:supplier
  column: ORD_PERIOD
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột ORD_PERIOD
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for ORD_PERIOD
- 'db2:supplier.ORD_PERIOD: top=0(1000)'
---

# supplier · ord period

**Semantic key:** `supplier__ord_period` · **Cột vật lý:** `ORD_PERIOD`

## Ý nghĩa nghiệp vụ

Cột ORD_PERIOD trên SUPPLIER. db2:supplier: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:supplier` | `ORD_PERIOD` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:supplier.ORD_PERIOD`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

