---
semantic_key: stk_dtl__frcust_sur
title: Frcust Sur (STK_DTL)
display_names:
- FRCUST_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCUST_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCUST_SUR'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Frcust Sur (STK_DTL)

**Semantic key:** `stk_dtl__frcust_sur` · **Cột vật lý:** `FRCUST_SUR`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — phát sinh liên quan khách (trả hàng / xuất KH) (thặng dư / chênh lệch tồn) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRCUST_SUR` | numeric | Đầu kỳ — movement: FRCUST_SUR |

## Ghi chú thêm

- Đầu kỳ — movement: FRCUST_SUR
