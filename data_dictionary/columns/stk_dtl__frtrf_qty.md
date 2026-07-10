---
semantic_key: stk_dtl__frtrf_qty
title: Số lượng (STK_DTL)
display_names:
- FRTRF_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRTRF_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRTRF_QTY'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (STK_DTL)

**Semantic key:** `stk_dtl__frtrf_qty` · **Cột vật lý:** `FRTRF_QTY`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — điều chuyển kho nội bộ (số lượng) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRTRF_QTY` | numeric | Đầu kỳ — movement: FRTRF_QTY |

## Ghi chú thêm

- Đầu kỳ — movement: FRTRF_QTY
