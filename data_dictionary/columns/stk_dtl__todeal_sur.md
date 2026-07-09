---
semantic_key: stk_dtl__todeal_sur
title: stk dtl · todeal sur
display_names:
- TODEAL_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: TODEAL_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TODEAL_SUR'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TODEAL_SUR
- 'db2:stk_dtl.TODEAL_SUR: top=0.00(1000)'
---

# stk dtl · todeal sur

**Semantic key:** `stk_dtl__todeal_sur` · **Cột vật lý:** `TODEAL_SUR`

## Ý nghĩa nghiệp vụ

Cột TODEAL_SUR trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TODEAL_SUR` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TODEAL_SUR`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TODEAL_SUR
