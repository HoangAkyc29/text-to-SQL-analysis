---
semantic_key: stk_dtl__frmul_qty
title: Số lượng (STK_DTL)
display_names:
- FRMUL_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRMUL_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRMUL_QTY'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (STK_DTL)

**Semantic key:** `stk_dtl__frmul_qty` · **Cột vật lý:** `FRMUL_QTY`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — ghép lô / nhân bản tồn (số lượng) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRMUL_QTY` | numeric | Đầu kỳ — movement: FRMUL_QTY |

## Ghi chú thêm

- Đầu kỳ — movement: FRMUL_QTY
