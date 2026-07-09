---
semantic_key: asso_inf__ratio
title: asso inf · ratio
display_names:
- RATIO
kind: measure
tables:
- ref: db2:asso_inf
  column: RATIO
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột RATIO
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for RATIO
- 'db2:asso_inf.RATIO: top=1(909), 0(91)'
---

# asso inf · ratio

**Semantic key:** `asso_inf__ratio` · **Cột vật lý:** `RATIO`

## Ý nghĩa nghiệp vụ

Cột RATIO trên ASSO_INF. db2:asso_inf: top 1, 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:asso_inf` | `RATIO` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:asso_inf.RATIO`
- Null rate trong sample: 0%
- Distinct ≈2; top: `1`×15, `0`×5

## Ghi chú thêm

