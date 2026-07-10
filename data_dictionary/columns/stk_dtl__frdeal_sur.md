---
semantic_key: stk_dtl__frdeal_sur
title: Frdeal Sur (STK_DTL)
display_names:
- FRDEAL_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRDEAL_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRDEAL_SUR'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Frdeal Sur (STK_DTL)

**Semantic key:** `stk_dtl__frdeal_sur` · **Cột vật lý:** `FRDEAL_SUR`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — xuất bán / giao dịch bán lẻ (thặng dư / chênh lệch tồn) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRDEAL_SUR` | numeric | Đầu kỳ — movement: FRDEAL_SUR |

## Ghi chú thêm

- Đầu kỳ — movement: FRDEAL_SUR
