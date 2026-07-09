---
semantic_key: stk_dtl__tocqty_qty
title: stk dtl · tocqty qty
display_names:
- TOCQTY_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCQTY_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCQTY_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOCQTY_QTY
- 'db2:stk_dtl.TOCQTY_QTY: top=0.000(1000)'
---

# stk dtl · tocqty qty

**Semantic key:** `stk_dtl__tocqty_qty` · **Cột vật lý:** `TOCQTY_QTY`

## Ý nghĩa nghiệp vụ

Cột TOCQTY_QTY trên STK_DTL. db2:stk_dtl: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOCQTY_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOCQTY_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Cuối kỳ — movement: TOCQTY_QTY
