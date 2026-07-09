---
semantic_key: stk_dtl__tomul_qty
title: stk dtl · tomul qty
display_names:
- TOMUL_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOMUL_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOMUL_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOMUL_QTY
- 'db2:stk_dtl.TOMUL_QTY: top=0.000(998), 295.376(1), 1008.000(1)'
---

# stk dtl · tomul qty

**Semantic key:** `stk_dtl__tomul_qty` · **Cột vật lý:** `TOMUL_QTY`

## Ý nghĩa nghiệp vụ

Cột TOMUL_QTY trên STK_DTL. db2:stk_dtl: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOMUL_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOMUL_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Cuối kỳ — movement: TOMUL_QTY
