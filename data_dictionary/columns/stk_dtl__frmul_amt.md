---
semantic_key: stk_dtl__frmul_amt
title: stk dtl · frmul amt
display_names:
- FRMUL_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRMUL_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRMUL_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRMUL_AMT
- 'db2:stk_dtl.FRMUL_AMT: top=0.00(995), 47071115.04(1), 3599868.06(1), 4267200.00(1),
  1342320.00(1)'
---

# stk dtl · frmul amt

**Semantic key:** `stk_dtl__frmul_amt` · **Cột vật lý:** `FRMUL_AMT`

## Ý nghĩa nghiệp vụ

Cột FRMUL_AMT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRMUL_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRMUL_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRMUL_AMT
