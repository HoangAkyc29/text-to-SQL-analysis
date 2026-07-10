---
semantic_key: stk_dtl__tocamt_amt
title: Số tiền / giá trị (STK_DTL)
display_names:
- TOCAMT_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCAMT_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCAMT_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (STK_DTL)

**Semantic key:** `stk_dtl__tocamt_amt` · **Cột vật lý:** `TOCAMT_AMT`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — tích lũy theo giá trị tiền (giá trị tồn (tiền)) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOCAMT_AMT` | numeric | Cuối kỳ — movement: TOCAMT_AMT |

## Ghi chú thêm

- Cuối kỳ — movement: TOCAMT_AMT
