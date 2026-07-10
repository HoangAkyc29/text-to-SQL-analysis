---
semantic_key: stk_dtl__tosupp_sur
title: Tosupp Sur (STK_DTL)
display_names:
- TOSUPP_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOSUPP_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOSUPP_SUR'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tosupp Sur (STK_DTL)

**Semantic key:** `stk_dtl__tosupp_sur` · **Cột vật lý:** `TOSUPP_SUR`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — nhập từ nhà cung cấp (thặng dư / chênh lệch tồn) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOSUPP_SUR` | numeric | Cuối kỳ — movement: TOSUPP_SUR |

## Ghi chú thêm

- Cuối kỳ — movement: TOSUPP_SUR
