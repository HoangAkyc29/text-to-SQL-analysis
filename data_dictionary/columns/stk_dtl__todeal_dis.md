---
semantic_key: stk_dtl__todeal_dis
title: Todeal Dis (STK_DTL)
display_names:
- TODEAL_DIS
kind: measure
tables:
- ref: db2:stk_dtl
  column: TODEAL_DIS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TODEAL_DIS'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Todeal Dis (STK_DTL)

**Semantic key:** `stk_dtl__todeal_dis` · **Cột vật lý:** `TODEAL_DIS`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — xuất bán / giao dịch bán lẻ (chiết khấu) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TODEAL_DIS` | numeric | Cuối kỳ — movement: TODEAL_DIS |

## Ghi chú thêm

- Cuối kỳ — movement: TODEAL_DIS
