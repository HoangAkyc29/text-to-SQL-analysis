---
semantic_key: stk_dtl__frtrf_qty
title: stk dtl · frtrf qty
display_names:
- FRTRF_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRTRF_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRTRF_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRTRF_QTY
- 'db2:stk_dtl.FRTRF_QTY: top=0.000(984), 136.000(2), 1200.000(1), 1020.000(1), 68.000(1)'
---

# stk dtl · frtrf qty

**Semantic key:** `stk_dtl__frtrf_qty` · **Cột vật lý:** `FRTRF_QTY`

## Ý nghĩa nghiệp vụ

Cột FRTRF_QTY trên STK_DTL. db2:stk_dtl: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRTRF_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRTRF_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRTRF_QTY
