---
semantic_key: stk_dtl__begin_qty
title: stk dtl · begin qty
display_names:
- BEGIN_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: BEGIN_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tồn đầu kỳ — số lượng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BEGIN_QTY
- 'db2:stk_dtl.BEGIN_QTY: top=0.000(810), 1.000(25), 2.000(13), 4.000(12), 3.000(9)'
---

# stk dtl · begin qty

**Semantic key:** `stk_dtl__begin_qty` · **Cột vật lý:** `BEGIN_QTY`

## Ý nghĩa nghiệp vụ

Cột BEGIN_QTY trên STK_DTL. db2:stk_dtl: top 1.000, 0.000, 2.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `BEGIN_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.BEGIN_QTY`
- Null rate trong sample: 0%
- Distinct ≈11; top: `1.000`×5, `0.000`×4, `2.000`×3, `98.000`×1, `99.000`×1, `-23.000`×1, `199.000`×1, `350.000`×1

## Ghi chú thêm

- Tồn đầu kỳ — số lượng
