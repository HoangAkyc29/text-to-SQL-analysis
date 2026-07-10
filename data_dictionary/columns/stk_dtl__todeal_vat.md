---
semantic_key: stk_dtl__todeal_vat
title: Todeal Vat (STK_DTL)
display_names:
- TODEAL_VAT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TODEAL_VAT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TODEAL_VAT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Todeal Vat (STK_DTL)

**Semantic key:** `stk_dtl__todeal_vat` · **Cột vật lý:** `TODEAL_VAT`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — xuất bán / giao dịch bán lẻ (thuế GTGT) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TODEAL_VAT` | numeric | Cuối kỳ — movement: TODEAL_VAT |

## Ghi chú thêm

- Cuối kỳ — movement: TODEAL_VAT
