---
semantic_key: stk_dtl__frcust_amt
title: Số tiền / giá trị (STK_DTL)
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
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (STK_DTL)

**Semantic key:** `stk_dtl__frcust_amt` · **Cột vật lý:** `FRCUST_AMT`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — phát sinh liên quan khách (trả hàng / xuất KH) (giá trị tồn (tiền)) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRCUST_AMT` | numeric | Đầu kỳ — movement: FRCUST_AMT |

## Ghi chú thêm

- Đầu kỳ — movement: FRCUST_AMT
