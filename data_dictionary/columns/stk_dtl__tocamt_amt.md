---
semantic_key: stk_dtl__tocamt_amt
title: stk dtl · tocamt amt
display_names:
- TOCAMT_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCAMT_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCAMT_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOCAMT_AMT
- 'db2:stk_dtl.TOCAMT_AMT: top=0.00(1000)'
---

# stk dtl · tocamt amt

**Semantic key:** `stk_dtl__tocamt_amt` · **Cột vật lý:** `TOCAMT_AMT`

## Ý nghĩa nghiệp vụ

Cột TOCAMT_AMT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOCAMT_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOCAMT_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TOCAMT_AMT
