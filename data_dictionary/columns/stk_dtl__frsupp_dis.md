---
semantic_key: stk_dtl__frsupp_dis
title: Frsupp Dis (STK_DTL)
display_names:
- FRSUPP_DIS
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRSUPP_DIS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRSUPP_DIS'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Frsupp Dis (STK_DTL)

**Semantic key:** `stk_dtl__frsupp_dis` · **Cột vật lý:** `FRSUPP_DIS`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — nhập từ nhà cung cấp (chiết khấu) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRSUPP_DIS` | numeric | Đầu kỳ — movement: FRSUPP_DIS |

## Ghi chú thêm

- Đầu kỳ — movement: FRSUPP_DIS
