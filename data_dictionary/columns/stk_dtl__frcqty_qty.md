---
semantic_key: stk_dtl__frcqty_qty
title: stk dtl · frcqty qty
display_names:
- FRCQTY_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCQTY_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCQTY_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRCQTY_QTY
- 'db2:stk_dtl.FRCQTY_QTY: top=0.000(1000)'
---

# stk dtl · frcqty qty

**Semantic key:** `stk_dtl__frcqty_qty` · **Cột vật lý:** `FRCQTY_QTY`

## Ý nghĩa nghiệp vụ

Cột FRCQTY_QTY trên STK_DTL. db2:stk_dtl: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRCQTY_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRCQTY_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRCQTY_QTY
