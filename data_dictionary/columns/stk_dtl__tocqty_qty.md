---
semantic_key: stk_dtl__tocqty_qty
title: Số lượng (STK_DTL)
display_names:
- TOCQTY_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCQTY_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCQTY_QTY'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (STK_DTL)

**Semantic key:** `stk_dtl__tocqty_qty` · **Cột vật lý:** `TOCQTY_QTY`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — tích lũy theo số lượng (số lượng) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOCQTY_QTY` | numeric | Cuối kỳ — movement: TOCQTY_QTY |

## Ghi chú thêm

- Cuối kỳ — movement: TOCQTY_QTY
