---
semantic_key: assolst__reverse
title: assolst · reverse
display_names:
- REVERSE
kind: flag
tables:
- ref: db2:assolst
  column: REVERSE
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột REVERSE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for REVERSE
- 'db2:assolst.REVERSE: top=True(1000)'
---

# assolst · reverse

**Semantic key:** `assolst__reverse` · **Cột vật lý:** `REVERSE`

## Ý nghĩa nghiệp vụ

Cột REVERSE trên ASSOLST. db2:assolst: top True.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:assolst` | `REVERSE` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:assolst.REVERSE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

## Ghi chú thêm

