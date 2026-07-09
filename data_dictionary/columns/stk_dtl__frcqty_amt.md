---
semantic_key: stk_dtl__frcqty_amt
title: stk dtl · frcqty amt
display_names:
- FRCQTY_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCQTY_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCQTY_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRCQTY_AMT
- 'db2:stk_dtl.FRCQTY_AMT: top=0.00(1000)'
---

# stk dtl · frcqty amt

**Semantic key:** `stk_dtl__frcqty_amt` · **Cột vật lý:** `FRCQTY_AMT`

## Ý nghĩa nghiệp vụ

Cột FRCQTY_AMT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRCQTY_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRCQTY_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRCQTY_AMT
