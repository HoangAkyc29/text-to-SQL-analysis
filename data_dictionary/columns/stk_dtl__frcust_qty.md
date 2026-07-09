---
semantic_key: stk_dtl__frcust_qty
title: stk dtl · frcust qty
display_names:
- FRCUST_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCUST_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCUST_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRCUST_QTY
- 'db2:stk_dtl.FRCUST_QTY: top=0.000(995), 204.000(1), 68.000(1), 476.000(1), 57.000(1)'
---

# stk dtl · frcust qty

**Semantic key:** `stk_dtl__frcust_qty` · **Cột vật lý:** `FRCUST_QTY`

## Ý nghĩa nghiệp vụ

Cột FRCUST_QTY trên STK_DTL. db2:stk_dtl: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRCUST_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRCUST_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRCUST_QTY
