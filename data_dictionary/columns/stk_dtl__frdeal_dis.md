---
semantic_key: stk_dtl__frdeal_dis
title: Frdeal Dis (STK_DTL)
display_names:
- FRDEAL_DIS
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRDEAL_DIS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRDEAL_DIS'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Frdeal Dis (STK_DTL)

**Semantic key:** `stk_dtl__frdeal_dis` · **Cột vật lý:** `FRDEAL_DIS`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — xuất bán / giao dịch bán lẻ (chiết khấu) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRDEAL_DIS` | numeric | Đầu kỳ — movement: FRDEAL_DIS |

## Ghi chú thêm

- Đầu kỳ — movement: FRDEAL_DIS
