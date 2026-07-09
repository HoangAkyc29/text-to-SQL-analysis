---
semantic_key: stk_dtl__frsupp_qty
title: stk dtl · frsupp qty
display_names:
- FRSUPP_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRSUPP_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRSUPP_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRSUPP_QTY
- 'db2:stk_dtl.FRSUPP_QTY: top=0.000(934), 816.000(3), 528.000(2), 1696.000(2), 204.000(2)'
---

# stk dtl · frsupp qty

**Semantic key:** `stk_dtl__frsupp_qty` · **Cột vật lý:** `FRSUPP_QTY`

## Ý nghĩa nghiệp vụ

Cột FRSUPP_QTY trên STK_DTL. db2:stk_dtl: top 0.000, 640.000, 13037.600.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRSUPP_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRSUPP_QTY`
- Null rate trong sample: 0%
- Distinct ≈3; top: `0.000`×18, `640.000`×1, `13037.600`×1

## Ghi chú thêm

- Đầu kỳ — movement: FRSUPP_QTY
