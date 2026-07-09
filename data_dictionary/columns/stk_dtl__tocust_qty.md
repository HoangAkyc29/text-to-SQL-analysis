---
semantic_key: stk_dtl__tocust_qty
title: stk dtl · tocust qty
display_names:
- TOCUST_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCUST_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCUST_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOCUST_QTY
- 'db2:stk_dtl.TOCUST_QTY: top=0.000(877), 68.000(16), 340.000(3), 136.000(3), 11.000(3)'
---

# stk dtl · tocust qty

**Semantic key:** `stk_dtl__tocust_qty` · **Cột vật lý:** `TOCUST_QTY`

## Ý nghĩa nghiệp vụ

Cột TOCUST_QTY trên STK_DTL. db2:stk_dtl: top 0.000, 476.000, 1159.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOCUST_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOCUST_QTY`
- Null rate trong sample: 0%
- Distinct ≈6; top: `0.000`×15, `476.000`×1, `1159.000`×1, `1274.000`×1, `13376.298`×1, `68.000`×1

## Ghi chú thêm

- Cuối kỳ — movement: TOCUST_QTY
