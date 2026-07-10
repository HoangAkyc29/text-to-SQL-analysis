---
semantic_key: stk_dtl__tocust_vat
title: Tocust Vat (STK_DTL)
display_names:
- TOCUST_VAT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCUST_VAT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCUST_VAT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tocust Vat (STK_DTL)

**Semantic key:** `stk_dtl__tocust_vat` · **Cột vật lý:** `TOCUST_VAT`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — phát sinh liên quan khách (trả hàng / xuất KH) (thuế GTGT) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOCUST_VAT` | numeric | Cuối kỳ — movement: TOCUST_VAT |

## Ghi chú thêm

- Cuối kỳ — movement: TOCUST_VAT
