---
semantic_key: stk_dtl__tobal_qty
title: stk dtl · tobal qty
display_names:
- TOBAL_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOBAL_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOBAL_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOBAL_QTY
- 'db2:stk_dtl.TOBAL_QTY: top=0.000(989), 36.664(1), 52.428(1), 15.232(1), 1000.000(1)'
---

# stk dtl · tobal qty

**Semantic key:** `stk_dtl__tobal_qty` · **Cột vật lý:** `TOBAL_QTY`

## Ý nghĩa nghiệp vụ

Cột TOBAL_QTY trên STK_DTL. db2:stk_dtl: top 0.000, 191.918.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOBAL_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOBAL_QTY`
- Null rate trong sample: 0%
- Distinct ≈2; top: `0.000`×19, `191.918`×1

## Ghi chú thêm

- Cuối kỳ — movement: TOBAL_QTY
