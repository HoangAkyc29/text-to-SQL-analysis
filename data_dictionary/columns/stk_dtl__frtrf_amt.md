---
semantic_key: stk_dtl__frtrf_amt
title: stk dtl · frtrf amt
display_names:
- FRTRF_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRTRF_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRTRF_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRTRF_AMT
- 'db2:stk_dtl.FRTRF_AMT: top=0.00(984), 15390000.00(1), 51944520.00(1), 7820000.00(1),
  32740776.00(1)'
---

# stk dtl · frtrf amt

**Semantic key:** `stk_dtl__frtrf_amt` · **Cột vật lý:** `FRTRF_AMT`

## Ý nghĩa nghiệp vụ

Cột FRTRF_AMT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRTRF_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRTRF_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRTRF_AMT
