---
semantic_key: supplier__fixsalepr
title: supplier · fixsalepr
display_names:
- FIXSALEPR
kind: measure
tables:
- ref: db2:supplier
  column: FIXSALEPR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột FIXSALEPR
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FIXSALEPR
- 'db2:supplier.FIXSALEPR: top=0(1000)'
---

# supplier · fixsalepr

**Semantic key:** `supplier__fixsalepr` · **Cột vật lý:** `FIXSALEPR`

## Ý nghĩa nghiệp vụ

Cột FIXSALEPR trên SUPPLIER. db2:supplier: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:supplier` | `FIXSALEPR` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:supplier.FIXSALEPR`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

