---
semantic_key: stk_dtl__frcust_qty
title: Số lượng (STK_DTL)
display_names:
- FRCUST_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCUST_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCUST_QTY'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (STK_DTL)

**Semantic key:** `stk_dtl__frcust_qty` · **Cột vật lý:** `FRCUST_QTY`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — phát sinh liên quan khách (trả hàng / xuất KH) (số lượng) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRCUST_QTY` | numeric | Đầu kỳ — movement: FRCUST_QTY |

## Ghi chú thêm

- Đầu kỳ — movement: FRCUST_QTY
