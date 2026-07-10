---
semantic_key: stk_dtl__tosupp_qty
title: Số lượng (STK_DTL)
display_names:
- TOSUPP_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOSUPP_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOSUPP_QTY'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (STK_DTL)

**Semantic key:** `stk_dtl__tosupp_qty` · **Cột vật lý:** `TOSUPP_QTY`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — nhập từ nhà cung cấp (số lượng) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOSUPP_QTY` | numeric | Cuối kỳ — movement: TOSUPP_QTY |

## Ghi chú thêm

- Cuối kỳ — movement: TOSUPP_QTY
