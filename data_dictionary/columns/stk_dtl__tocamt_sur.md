---
semantic_key: stk_dtl__tocamt_sur
title: Tocamt Sur (STK_DTL)
display_names:
- TOCAMT_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCAMT_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCAMT_SUR'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tocamt Sur (STK_DTL)

**Semantic key:** `stk_dtl__tocamt_sur` · **Cột vật lý:** `TOCAMT_SUR`

## Ý nghĩa nghiệp vụ

Phát sinh cuối kỳ — tích lũy theo giá trị tiền (thặng dư / chênh lệch tồn) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `TOCAMT_SUR` | numeric | Cuối kỳ — movement: TOCAMT_SUR |

## Ghi chú thêm

- Cuối kỳ — movement: TOCAMT_SUR
