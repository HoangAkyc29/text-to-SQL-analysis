---
semantic_key: assolst__fix_ratio
title: assolst · fix ratio
display_names:
- FIX_RATIO
kind: flag
tables:
- ref: db2:assolst
  column: FIX_RATIO
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột FIX_RATIO
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FIX_RATIO
- 'db2:assolst.FIX_RATIO: top=False(1000)'
---

# assolst · fix ratio

**Semantic key:** `assolst__fix_ratio` · **Cột vật lý:** `FIX_RATIO`

## Ý nghĩa nghiệp vụ

Cột FIX_RATIO trên ASSOLST. db2:assolst: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:assolst` | `FIX_RATIO` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:assolst.FIX_RATIO`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

