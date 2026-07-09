---
semantic_key: stk_dtl__frcust_sur
title: stk dtl · frcust sur
display_names:
- FRCUST_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCUST_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCUST_SUR'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRCUST_SUR
- 'db2:stk_dtl.FRCUST_SUR: top=0.00(995), 2462461.56(1), 517051.60(1), 25228000.00(1),
  34666363.74(1)'
---

# stk dtl · frcust sur

**Semantic key:** `stk_dtl__frcust_sur` · **Cột vật lý:** `FRCUST_SUR`

## Ý nghĩa nghiệp vụ

Cột FRCUST_SUR trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRCUST_SUR` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRCUST_SUR`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRCUST_SUR
