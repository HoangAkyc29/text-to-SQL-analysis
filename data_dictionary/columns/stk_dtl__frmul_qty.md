---
semantic_key: stk_dtl__frmul_qty
title: stk dtl · frmul qty
display_names:
- FRMUL_QTY
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRMUL_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRMUL_QTY'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRMUL_QTY
- 'db2:stk_dtl.FRMUL_QTY: top=0.000(995), 816.000(1), 114.000(1), 196.000(1), 204.000(1)'
---

# stk dtl · frmul qty

**Semantic key:** `stk_dtl__frmul_qty` · **Cột vật lý:** `FRMUL_QTY`

## Ý nghĩa nghiệp vụ

Cột FRMUL_QTY trên STK_DTL. db2:stk_dtl: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRMUL_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRMUL_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRMUL_QTY
