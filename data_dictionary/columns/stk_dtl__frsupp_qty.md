---
semantic_key: stk_dtl__frsupp_qty
title: Số lượng (STK_DTL)
display_names:
- FRSUPP_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRSUPP_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRSUPP_QTY'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (STK_DTL)

**Semantic key:** `stk_dtl__frsupp_qty` · **Cột vật lý:** `FRSUPP_QTY`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — nhập từ nhà cung cấp (số lượng) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRSUPP_QTY` | numeric | Đầu kỳ — movement: FRSUPP_QTY |

## Ghi chú thêm

- Đầu kỳ — movement: FRSUPP_QTY
