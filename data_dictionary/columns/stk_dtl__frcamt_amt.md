---
semantic_key: stk_dtl__frcamt_amt
title: Số tiền / giá trị (STK_DTL)
display_names:
- FRCAMT_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCAMT_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCAMT_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (STK_DTL)

**Semantic key:** `stk_dtl__frcamt_amt` · **Cột vật lý:** `FRCAMT_AMT`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — tích lũy theo giá trị tiền (giá trị tồn (tiền)) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRCAMT_AMT` | numeric | Đầu kỳ — movement: FRCAMT_AMT |

## Ghi chú thêm

- Đầu kỳ — movement: FRCAMT_AMT
