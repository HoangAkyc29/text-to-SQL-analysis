---
semantic_key: stk_dtl__frsupp_amt
title: Số tiền / giá trị (STK_DTL)
display_names:
- FRSUPP_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRSUPP_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRSUPP_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (STK_DTL)

**Semantic key:** `stk_dtl__frsupp_amt` · **Cột vật lý:** `FRSUPP_AMT`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — nhập từ nhà cung cấp (giá trị tồn (tiền)) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRSUPP_AMT` | numeric | Đầu kỳ — movement: FRSUPP_AMT |

## Ghi chú thêm

- Đầu kỳ — movement: FRSUPP_AMT
