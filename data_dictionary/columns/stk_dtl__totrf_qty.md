---
semantic_key: stk_dtl__totrf_qty
title: stk dtl · totrf qty
display_names:
- TOTRF_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOTRF_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOTRF_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOTRF_QTY
- 'db2:stk_dtl.TOTRF_QTY: top=0.000(980), 68.000(3), 272.000(2), 2916.000(1), 816.000(1)'
---

# stk dtl · totrf qty

**Semantic key:** `stk_dtl__totrf_qty` · **Cột vật lý:** `TOTRF_QTY`

## Ý nghĩa nghiệp vụ

Cột TOTRF_QTY trên STK_DTL. db2:stk_dtl: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOTRF_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOTRF_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Cuối kỳ — movement: TOTRF_QTY
