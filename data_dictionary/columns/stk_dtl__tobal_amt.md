---
semantic_key: stk_dtl__tobal_amt
title: stk dtl · tobal amt
display_names:
- TOBAL_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOBAL_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOBAL_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOBAL_AMT
- 'db2:stk_dtl.TOBAL_AMT: top=0.00(989), 1466560.00(1), 4943211.72(1), 1218560.00(1),
  73000000.00(1)'
---

# stk dtl · tobal amt

**Semantic key:** `stk_dtl__tobal_amt` · **Cột vật lý:** `TOBAL_AMT`

## Ý nghĩa nghiệp vụ

Cột TOBAL_AMT trên STK_DTL. db2:stk_dtl: top 0.00, 6836026.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOBAL_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOBAL_AMT`
- Null rate trong sample: 0%
- Distinct ≈2; top: `0.00`×19, `6836026.00`×1

## Ghi chú thêm

- Cuối kỳ — movement: TOBAL_AMT
