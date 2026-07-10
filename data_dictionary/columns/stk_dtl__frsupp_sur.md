---
semantic_key: stk_dtl__frsupp_sur
title: Frsupp Sur (STK_DTL)
display_names:
- FRSUPP_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRSUPP_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRSUPP_SUR'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Frsupp Sur (STK_DTL)

**Semantic key:** `stk_dtl__frsupp_sur` · **Cột vật lý:** `FRSUPP_SUR`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — nhập từ nhà cung cấp (thặng dư / chênh lệch tồn) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRSUPP_SUR` | numeric | Đầu kỳ — movement: FRSUPP_SUR |

## Ghi chú thêm

- Đầu kỳ — movement: FRSUPP_SUR
