---
semantic_key: stk_dtl__todeal_com
title: Todeal Com (STK_DTL)
display_names:
- TODEAL_COM
kind: measure
tables:
- ref: db2:stk_dtl
  column: TODEAL_COM
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TODEAL_COM'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Todeal Com (STK_DTL)

**Semantic key:** `stk_dtl__todeal_com` · **Cột vật lý:** `TODEAL_COM`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — xuất bán / giao dịch bán lẻ (hoa hồng / chi phí liên quan) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TODEAL_COM` | numeric | Cuối kỳ — movement: TODEAL_COM |

## Ghi chú thêm

- Cuối kỳ — movement: TODEAL_COM
