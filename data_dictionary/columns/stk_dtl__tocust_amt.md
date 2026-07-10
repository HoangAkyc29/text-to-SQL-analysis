---
semantic_key: stk_dtl__tocust_amt
title: Số tiền / giá trị (STK_DTL)
display_names:
- TOCUST_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCUST_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCUST_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (STK_DTL)

**Semantic key:** `stk_dtl__tocust_amt` · **Cột vật lý:** `TOCUST_AMT`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — phát sinh liên quan khách (trả hàng / xuất KH) (giá trị tồn (tiền)) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOCUST_AMT` | numeric | Cuối kỳ — movement: TOCUST_AMT |

## Ghi chú thêm

- Cuối kỳ — movement: TOCUST_AMT
