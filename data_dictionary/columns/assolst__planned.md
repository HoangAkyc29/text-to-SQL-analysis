---
semantic_key: assolst__planned
title: assolst · planned
display_names:
- Planned
kind: flag
tables:
- ref: db2:assolst
  column: Planned
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột Planned
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for Planned
- 'db2:assolst.Planned: top=False(1000)'
---

# assolst · planned

**Semantic key:** `assolst__planned` · **Cột vật lý:** `Planned`

## Ý nghĩa nghiệp vụ

Cột PLANNED trên ASSOLST. db2:assolst: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:assolst` | `Planned` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:assolst.Planned`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

- Cột Planned
