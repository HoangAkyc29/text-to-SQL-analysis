---
semantic_key: stk_dtl__totrf_amt
title: stk dtl · totrf amt
display_names:
- TOTRF_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOTRF_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOTRF_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOTRF_AMT
- 'db2:stk_dtl.TOTRF_AMT: top=0.00(980), 153401115.48(1), 46240000.00(1), 45325095.36(1),
  575000.00(1)'
---

# stk dtl · totrf amt

**Semantic key:** `stk_dtl__totrf_amt` · **Cột vật lý:** `TOTRF_AMT`

## Ý nghĩa nghiệp vụ

Cột TOTRF_AMT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOTRF_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOTRF_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TOTRF_AMT
