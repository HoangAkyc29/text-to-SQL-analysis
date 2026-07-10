---
semantic_key: stk_dtl__frbal_qty
title: Số lượng (STK_DTL)
display_names:
- FRBAL_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRBAL_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRBAL_QTY'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (STK_DTL)

**Semantic key:** `stk_dtl__frbal_qty` · **Cột vật lý:** `FRBAL_QTY`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — điều chỉnh cân bằng kỳ (số lượng) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRBAL_QTY` | numeric | Đầu kỳ — movement: FRBAL_QTY |

## Ghi chú thêm

- Đầu kỳ — movement: FRBAL_QTY
