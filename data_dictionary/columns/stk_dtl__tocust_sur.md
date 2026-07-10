---
semantic_key: stk_dtl__tocust_sur
title: Tocust Sur (STK_DTL)
display_names:
- TOCUST_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCUST_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCUST_SUR'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tocust Sur (STK_DTL)

**Semantic key:** `stk_dtl__tocust_sur` · **Cột vật lý:** `TOCUST_SUR`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — phát sinh liên quan khách (trả hàng / xuất KH) (thặng dư / chênh lệch tồn) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOCUST_SUR` | numeric | Cuối kỳ — movement: TOCUST_SUR |

## Ghi chú thêm

- Cuối kỳ — movement: TOCUST_SUR
