---
semantic_key: stk_dtl__tosupp_com
title: Tosupp Com (STK_DTL)
display_names:
- TOSUPP_COM
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOSUPP_COM
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOSUPP_COM'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tosupp Com (STK_DTL)

**Semantic key:** `stk_dtl__tosupp_com` · **Cột vật lý:** `TOSUPP_COM`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — nhập từ nhà cung cấp (hoa hồng / chi phí liên quan) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOSUPP_COM` | numeric | Cuối kỳ — movement: TOSUPP_COM |

## Ghi chú thêm

- Cuối kỳ — movement: TOSUPP_COM
