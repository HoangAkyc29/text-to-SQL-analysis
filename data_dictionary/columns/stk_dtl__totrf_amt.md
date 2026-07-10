---
semantic_key: stk_dtl__totrf_amt
title: Số tiền / giá trị (STK_DTL)
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
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (STK_DTL)

**Semantic key:** `stk_dtl__totrf_amt` · **Cột vật lý:** `TOTRF_AMT`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — điều chuyển kho nội bộ (giá trị tồn (tiền)) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOTRF_AMT` | numeric | Cuối kỳ — movement: TOTRF_AMT |

## Ghi chú thêm

- Cuối kỳ — movement: TOTRF_AMT
