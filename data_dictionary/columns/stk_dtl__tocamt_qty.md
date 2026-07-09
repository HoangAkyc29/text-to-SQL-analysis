---
semantic_key: stk_dtl__tocamt_qty
title: stk dtl · tocamt qty
display_names:
- TOCAMT_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCAMT_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCAMT_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOCAMT_QTY
- 'db2:stk_dtl.TOCAMT_QTY: top=0.000(1000)'
---

# stk dtl · tocamt qty

**Semantic key:** `stk_dtl__tocamt_qty` · **Cột vật lý:** `TOCAMT_QTY`

## Ý nghĩa nghiệp vụ

Cột TOCAMT_QTY trên STK_DTL. db2:stk_dtl: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOCAMT_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOCAMT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Cuối kỳ — movement: TOCAMT_QTY
