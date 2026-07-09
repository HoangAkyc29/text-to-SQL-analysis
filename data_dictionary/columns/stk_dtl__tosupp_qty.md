---
semantic_key: stk_dtl__tosupp_qty
title: stk dtl · tosupp qty
display_names:
- TOSUPP_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOSUPP_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOSUPP_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOSUPP_QTY
- 'db2:stk_dtl.TOSUPP_QTY: top=0.000(999), 136.000(1)'
---

# stk dtl · tosupp qty

**Semantic key:** `stk_dtl__tosupp_qty` · **Cột vật lý:** `TOSUPP_QTY`

## Ý nghĩa nghiệp vụ

Cột TOSUPP_QTY trên STK_DTL. db2:stk_dtl: top 0.000, 640.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOSUPP_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOSUPP_QTY`
- Null rate trong sample: 0%
- Distinct ≈2; top: `0.000`×19, `640.000`×1

## Ghi chú thêm

- Cuối kỳ — movement: TOSUPP_QTY
