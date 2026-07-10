---
semantic_key: stk_dtl__frdeal_com
title: Frdeal Com (STK_DTL)
display_names:
- FRDEAL_COM
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRDEAL_COM
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRDEAL_COM'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Frdeal Com (STK_DTL)

**Semantic key:** `stk_dtl__frdeal_com` · **Cột vật lý:** `FRDEAL_COM`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — xuất bán / giao dịch bán lẻ (hoa hồng / chi phí liên quan) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRDEAL_COM` | numeric | Đầu kỳ — movement: FRDEAL_COM |

## Ghi chú thêm

- Đầu kỳ — movement: FRDEAL_COM
