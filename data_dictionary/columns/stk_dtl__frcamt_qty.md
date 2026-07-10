---
semantic_key: stk_dtl__frcamt_qty
title: Số lượng (STK_DTL)
display_names:
- FRCAMT_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCAMT_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCAMT_QTY'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (STK_DTL)

**Semantic key:** `stk_dtl__frcamt_qty` · **Cột vật lý:** `FRCAMT_QTY`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — tích lũy theo giá trị tiền (số lượng) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRCAMT_QTY` | numeric | Đầu kỳ — movement: FRCAMT_QTY |

## Ghi chú thêm

- Đầu kỳ — movement: FRCAMT_QTY
