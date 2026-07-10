---
semantic_key: stk_dtl__frcust_vat
title: Frcust Vat (STK_DTL)
display_names:
- FRCUST_VAT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCUST_VAT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCUST_VAT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Frcust Vat (STK_DTL)

**Semantic key:** `stk_dtl__frcust_vat` · **Cột vật lý:** `FRCUST_VAT`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — phát sinh liên quan khách (trả hàng / xuất KH) (thuế GTGT) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRCUST_VAT` | numeric | Đầu kỳ — movement: FRCUST_VAT |

## Ghi chú thêm

- Đầu kỳ — movement: FRCUST_VAT
