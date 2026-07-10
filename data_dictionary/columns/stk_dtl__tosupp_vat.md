---
semantic_key: stk_dtl__tosupp_vat
title: Tosupp Vat (STK_DTL)
display_names:
- TOSUPP_VAT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOSUPP_VAT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOSUPP_VAT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tosupp Vat (STK_DTL)

**Semantic key:** `stk_dtl__tosupp_vat` · **Cột vật lý:** `TOSUPP_VAT`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — nhập từ nhà cung cấp (thuế GTGT) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOSUPP_VAT` | numeric | Cuối kỳ — movement: TOSUPP_VAT |

## Ghi chú thêm

- Cuối kỳ — movement: TOSUPP_VAT
