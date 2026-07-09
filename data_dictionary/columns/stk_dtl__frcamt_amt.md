---
semantic_key: stk_dtl__frcamt_amt
title: stk dtl · frcamt amt
display_names:
- FRCAMT_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCAMT_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCAMT_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRCAMT_AMT
- 'db2:stk_dtl.FRCAMT_AMT: top=0.00(1000)'
---

# stk dtl · frcamt amt

**Semantic key:** `stk_dtl__frcamt_amt` · **Cột vật lý:** `FRCAMT_AMT`

## Ý nghĩa nghiệp vụ

Cột FRCAMT_AMT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRCAMT_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRCAMT_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRCAMT_AMT
