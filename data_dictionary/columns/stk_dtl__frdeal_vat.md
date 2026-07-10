---
semantic_key: stk_dtl__frdeal_vat
title: Frdeal Vat (STK_DTL)
display_names:
- FRDEAL_VAT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRDEAL_VAT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRDEAL_VAT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Frdeal Vat (STK_DTL)

**Semantic key:** `stk_dtl__frdeal_vat` · **Cột vật lý:** `FRDEAL_VAT`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — xuất bán / giao dịch bán lẻ (thuế GTGT) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRDEAL_VAT` | numeric | Đầu kỳ — movement: FRDEAL_VAT |

## Ghi chú thêm

- Đầu kỳ — movement: FRDEAL_VAT
