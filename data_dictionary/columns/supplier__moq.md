---
semantic_key: supplier__moq
title: supplier · moq
display_names:
- MOQ
kind: measure
tables:
- ref: db2:supplier
  column: MOQ
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột MOQ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for MOQ
- 'db2:supplier.MOQ: top=0.000(1000)'
---

# supplier · moq

**Semantic key:** `supplier__moq` · **Cột vật lý:** `MOQ`

## Ý nghĩa nghiệp vụ

Cột MOQ trên SUPPLIER. db2:supplier: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:supplier` | `MOQ` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:supplier.MOQ`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

