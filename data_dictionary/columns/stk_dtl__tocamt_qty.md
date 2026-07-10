---
semantic_key: stk_dtl__tocamt_qty
title: Số lượng (STK_DTL)
display_names:
- TOCAMT_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCAMT_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCAMT_QTY'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (STK_DTL)

**Semantic key:** `stk_dtl__tocamt_qty` · **Cột vật lý:** `TOCAMT_QTY`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — tích lũy theo giá trị tiền (số lượng) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOCAMT_QTY` | numeric | Cuối kỳ — movement: TOCAMT_QTY |

## Ghi chú thêm

- Cuối kỳ — movement: TOCAMT_QTY
