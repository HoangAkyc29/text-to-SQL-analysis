---
semantic_key: supplier__moa
title: supplier · moa
display_names:
- MOA
kind: measure
tables:
- ref: db2:supplier
  column: MOA
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột MOA
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for MOA
- 'db2:supplier.MOA: top=0.00(1000)'
---

# supplier · moa

**Semantic key:** `supplier__moa` · **Cột vật lý:** `MOA`

## Ý nghĩa nghiệp vụ

Cột MOA trên SUPPLIER. db2:supplier: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:supplier` | `MOA` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:supplier.MOA`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

