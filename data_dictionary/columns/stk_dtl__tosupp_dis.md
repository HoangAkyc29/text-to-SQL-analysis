---
semantic_key: stk_dtl__tosupp_dis
title: Tosupp Dis (STK_DTL)
display_names:
- TOSUPP_DIS
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOSUPP_DIS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOSUPP_DIS'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tosupp Dis (STK_DTL)

**Semantic key:** `stk_dtl__tosupp_dis` · **Cột vật lý:** `TOSUPP_DIS`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — nhập từ nhà cung cấp (chiết khấu) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOSUPP_DIS` | numeric | Cuối kỳ — movement: TOSUPP_DIS |

## Ghi chú thêm

- Cuối kỳ — movement: TOSUPP_DIS
