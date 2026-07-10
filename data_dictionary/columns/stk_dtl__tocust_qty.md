---
semantic_key: stk_dtl__tocust_qty
title: Số lượng (STK_DTL)
display_names:
- TOCUST_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCUST_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCUST_QTY'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (STK_DTL)

**Semantic key:** `stk_dtl__tocust_qty` · **Cột vật lý:** `TOCUST_QTY`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — phát sinh liên quan khách (trả hàng / xuất KH) (số lượng) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOCUST_QTY` | numeric | Cuối kỳ — movement: TOCUST_QTY |

## Ghi chú thêm

- Cuối kỳ — movement: TOCUST_QTY
