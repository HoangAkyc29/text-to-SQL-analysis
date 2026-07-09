---
semantic_key: stk_dtl__todeal_amt
title: stk dtl · todeal amt
display_names:
- TODEAL_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TODEAL_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TODEAL_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TODEAL_AMT
- 'db2:stk_dtl.TODEAL_AMT: top=0.00(999), 18418400.00(1)'
---

# stk dtl · todeal amt

**Semantic key:** `stk_dtl__todeal_amt` · **Cột vật lý:** `TODEAL_AMT`

## Ý nghĩa nghiệp vụ

Cột TODEAL_AMT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TODEAL_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TODEAL_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TODEAL_AMT
