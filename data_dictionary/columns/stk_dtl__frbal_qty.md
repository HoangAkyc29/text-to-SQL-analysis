---
semantic_key: stk_dtl__frbal_qty
title: stk dtl · frbal qty
display_names:
- FRBAL_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRBAL_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRBAL_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRBAL_QTY
- 'db2:stk_dtl.FRBAL_QTY: top=0.000(999), 3.808(1)'
---

# stk dtl · frbal qty

**Semantic key:** `stk_dtl__frbal_qty` · **Cột vật lý:** `FRBAL_QTY`

## Ý nghĩa nghiệp vụ

Cột FRBAL_QTY trên STK_DTL. db2:stk_dtl: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRBAL_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRBAL_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRBAL_QTY
