---
semantic_key: stk_dtl__frsupp_com
title: Frsupp Com (STK_DTL)
display_names:
- FRSUPP_COM
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRSUPP_COM
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRSUPP_COM'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Frsupp Com (STK_DTL)

**Semantic key:** `stk_dtl__frsupp_com` · **Cột vật lý:** `FRSUPP_COM`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — nhập từ nhà cung cấp (hoa hồng / chi phí liên quan) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRSUPP_COM` | numeric | Đầu kỳ — movement: FRSUPP_COM |

## Ghi chú thêm

- Đầu kỳ — movement: FRSUPP_COM
