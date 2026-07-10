---
semantic_key: stk_dtl__todeal_sur
title: Todeal Sur (STK_DTL)
display_names:
- TODEAL_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: TODEAL_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TODEAL_SUR'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Todeal Sur (STK_DTL)

**Semantic key:** `stk_dtl__todeal_sur` · **Cột vật lý:** `TODEAL_SUR`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — xuất bán / giao dịch bán lẻ (thặng dư / chênh lệch tồn) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TODEAL_SUR` | numeric | Cuối kỳ — movement: TODEAL_SUR |

## Ghi chú thêm

- Cuối kỳ — movement: TODEAL_SUR
