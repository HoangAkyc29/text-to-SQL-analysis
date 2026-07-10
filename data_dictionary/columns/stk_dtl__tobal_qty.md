---
semantic_key: stk_dtl__tobal_qty
title: Số lượng (STK_DTL)
display_names:
- TOBAL_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOBAL_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOBAL_QTY'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (STK_DTL)

**Semantic key:** `stk_dtl__tobal_qty` · **Cột vật lý:** `TOBAL_QTY`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — điều chỉnh cân bằng kỳ (số lượng) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOBAL_QTY` | numeric | Cuối kỳ — movement: TOBAL_QTY |

## Ghi chú thêm

- Cuối kỳ — movement: TOBAL_QTY
