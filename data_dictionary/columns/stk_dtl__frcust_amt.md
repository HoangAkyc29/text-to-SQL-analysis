---
semantic_key: stk_dtl__frcust_amt
title: stk dtl · frcust amt
display_names:
- FRCUST_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCUST_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCUST_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRCUST_AMT
- 'db2:stk_dtl.FRCUST_AMT: top=0.00(995), 10570872.00(1), 2505170.32(1), 59500000.00(1),
  111409090.65(1)'
---

# stk dtl · frcust amt

**Semantic key:** `stk_dtl__frcust_amt` · **Cột vật lý:** `FRCUST_AMT`

## Ý nghĩa nghiệp vụ

Cột FRCUST_AMT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRCUST_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRCUST_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRCUST_AMT
