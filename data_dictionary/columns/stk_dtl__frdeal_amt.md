---
semantic_key: stk_dtl__frdeal_amt
title: Số tiền / giá trị (STK_DTL)
display_names:
- FRDEAL_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRDEAL_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRDEAL_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (STK_DTL)

**Semantic key:** `stk_dtl__frdeal_amt` · **Cột vật lý:** `FRDEAL_AMT`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — xuất bán / giao dịch bán lẻ (giá trị tồn (tiền)) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRDEAL_AMT` | numeric | Đầu kỳ — movement: FRDEAL_AMT |

## Ghi chú thêm

- Đầu kỳ — movement: FRDEAL_AMT
