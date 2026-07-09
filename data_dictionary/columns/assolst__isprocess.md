---
semantic_key: assolst__isprocess
title: assolst · isprocess
display_names:
- IsProcess
kind: flag
tables:
- ref: db2:assolst
  column: IsProcess
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột IsProcess
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for IsProcess
- 'db2:assolst.IsProcess: top=False(1000)'
---

# assolst · isprocess

**Semantic key:** `assolst__isprocess` · **Cột vật lý:** `IsProcess`

## Ý nghĩa nghiệp vụ

Cột ISPROCESS trên ASSOLST. db2:assolst: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:assolst` | `IsProcess` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:assolst.IsProcess`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

- Cột IsProcess
