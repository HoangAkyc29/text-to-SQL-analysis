---
semantic_key: stk_dtl__frbal_amt
title: stk dtl · frbal amt
display_names:
- FRBAL_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRBAL_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRBAL_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRBAL_AMT
- 'db2:stk_dtl.FRBAL_AMT: top=0.00(999), 171360.00(1)'
---

# stk dtl · frbal amt

**Semantic key:** `stk_dtl__frbal_amt` · **Cột vật lý:** `FRBAL_AMT`

## Ý nghĩa nghiệp vụ

Cột FRBAL_AMT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRBAL_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRBAL_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRBAL_AMT
