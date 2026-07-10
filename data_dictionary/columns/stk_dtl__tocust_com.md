---
semantic_key: stk_dtl__tocust_com
title: Tocust Com (STK_DTL)
display_names:
- TOCUST_COM
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCUST_COM
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCUST_COM'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tocust Com (STK_DTL)

**Semantic key:** `stk_dtl__tocust_com` · **Cột vật lý:** `TOCUST_COM`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — phát sinh liên quan khách (trả hàng / xuất KH) (hoa hồng / chi phí liên quan) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOCUST_COM` | numeric | Cuối kỳ — movement: TOCUST_COM |

## Ghi chú thêm

- Cuối kỳ — movement: TOCUST_COM
