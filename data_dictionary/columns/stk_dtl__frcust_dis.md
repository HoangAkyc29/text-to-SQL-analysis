---
semantic_key: stk_dtl__frcust_dis
title: Frcust Dis (STK_DTL)
display_names:
- FRCUST_DIS
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCUST_DIS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCUST_DIS'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Frcust Dis (STK_DTL)

**Semantic key:** `stk_dtl__frcust_dis` · **Cột vật lý:** `FRCUST_DIS`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — phát sinh liên quan khách (trả hàng / xuất KH) (chiết khấu) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRCUST_DIS` | numeric | Đầu kỳ — movement: FRCUST_DIS |

## Ghi chú thêm

- Đầu kỳ — movement: FRCUST_DIS
