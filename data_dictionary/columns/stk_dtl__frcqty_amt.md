---
semantic_key: stk_dtl__frcqty_amt
title: Số tiền / giá trị (STK_DTL)
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
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (STK_DTL)

**Semantic key:** `stk_dtl__frcqty_amt` · **Cột vật lý:** `FRCQTY_AMT`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — tích lũy theo số lượng (giá trị tồn (tiền)) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRCQTY_AMT` | numeric | Đầu kỳ — movement: FRCQTY_AMT |

## Ghi chú thêm

- Đầu kỳ — movement: FRCQTY_AMT
