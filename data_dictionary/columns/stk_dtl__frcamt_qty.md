---
semantic_key: stk_dtl__frcamt_qty
title: stk dtl · frcamt qty
display_names:
- FRCAMT_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCAMT_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCAMT_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRCAMT_QTY
- 'db2:stk_dtl.FRCAMT_QTY: top=0.000(1000)'
---

# stk dtl · frcamt qty

**Semantic key:** `stk_dtl__frcamt_qty` · **Cột vật lý:** `FRCAMT_QTY`

## Ý nghĩa nghiệp vụ

Cột FRCAMT_QTY trên STK_DTL. db2:stk_dtl: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRCAMT_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRCAMT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRCAMT_QTY
