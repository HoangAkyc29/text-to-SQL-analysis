---
semantic_key: stk_dtl__frcamt_sur
title: Frcamt Sur (STK_DTL)
display_names:
- FRCAMT_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCAMT_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCAMT_SUR'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Frcamt Sur (STK_DTL)

**Semantic key:** `stk_dtl__frcamt_sur` · **Cột vật lý:** `FRCAMT_SUR`

## Ý nghĩa nghiệp vụ

Phát sinh đầu kỳ — tích lũy theo giá trị tiền (thặng dư / chênh lệch tồn) trên sổ chi tiết tồn kho STK_DTL. Grain: STK_ID × SKU_ID × kỳ (PRD_CODE).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:stk_dtl` | `FRCAMT_SUR` | numeric | Đầu kỳ — movement: FRCAMT_SUR |

## Ghi chú thêm

- Đầu kỳ — movement: FRCAMT_SUR
