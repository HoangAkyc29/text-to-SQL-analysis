---
semantic_key: stk_dtl__frsupp_vat
title: Frsupp Vat (STK_DTL)
display_names:
- FRSUPP_VAT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRSUPP_VAT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRSUPP_VAT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Frsupp Vat (STK_DTL)

**Semantic key:** `stk_dtl__frsupp_vat` · **Cột vật lý:** `FRSUPP_VAT`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — nhập từ nhà cung cấp (thuế GTGT) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRSUPP_VAT` | numeric | Đầu kỳ — movement: FRSUPP_VAT |

## Ghi chú thêm

- Đầu kỳ — movement: FRSUPP_VAT
