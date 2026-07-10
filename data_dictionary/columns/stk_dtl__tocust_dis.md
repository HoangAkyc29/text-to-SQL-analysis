---
semantic_key: stk_dtl__tocust_dis
title: Tocust Dis (STK_DTL)
display_names:
- TOCUST_DIS
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCUST_DIS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCUST_DIS'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tocust Dis (STK_DTL)

**Semantic key:** `stk_dtl__tocust_dis` · **Cột vật lý:** `TOCUST_DIS`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — phát sinh liên quan khách (trả hàng / xuất KH) (chiết khấu) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOCUST_DIS` | numeric | Cuối kỳ — movement: TOCUST_DIS |

## Ghi chú thêm

- Cuối kỳ — movement: TOCUST_DIS
