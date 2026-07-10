---
semantic_key: stk_dtl__frcust_com
title: Frcust Com (STK_DTL)
display_names:
- FRCUST_COM
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCUST_COM
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCUST_COM'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Frcust Com (STK_DTL)

**Semantic key:** `stk_dtl__frcust_com` · **Cột vật lý:** `FRCUST_COM`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — phát sinh liên quan khách (trả hàng / xuất KH) (hoa hồng / chi phí liên quan) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRCUST_COM` | numeric | Đầu kỳ — movement: FRCUST_COM |

## Ghi chú thêm

- Đầu kỳ — movement: FRCUST_COM
