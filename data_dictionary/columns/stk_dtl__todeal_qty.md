---
semantic_key: stk_dtl__todeal_qty
title: stk dtl · todeal qty
display_names:
- TODEAL_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: TODEAL_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TODEAL_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TODEAL_QTY
- 'db2:stk_dtl.TODEAL_QTY: top=0.000(999), 141.680(1)'
---

# stk dtl · todeal qty

**Semantic key:** `stk_dtl__todeal_qty` · **Cột vật lý:** `TODEAL_QTY`

## Ý nghĩa nghiệp vụ

Cột TODEAL_QTY trên STK_DTL. db2:stk_dtl: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TODEAL_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TODEAL_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Cuối kỳ — movement: TODEAL_QTY
