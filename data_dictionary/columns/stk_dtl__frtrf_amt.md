---
semantic_key: stk_dtl__frtrf_amt
title: Số tiền / giá trị (STK_DTL)
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
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (STK_DTL)

**Semantic key:** `stk_dtl__frtrf_amt` · **Cột vật lý:** `FRTRF_AMT`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — điều chuyển kho nội bộ (giá trị tồn (tiền)) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRTRF_AMT` | numeric | Đầu kỳ — movement: FRTRF_AMT |

## Ghi chú thêm

- Đầu kỳ — movement: FRTRF_AMT
