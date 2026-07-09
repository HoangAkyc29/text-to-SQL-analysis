---
semantic_key: stk_dtl__tocamt_sur
title: stk dtl · tocamt sur
display_names:
- TOCAMT_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCAMT_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCAMT_SUR'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOCAMT_SUR
- 'db2:stk_dtl.TOCAMT_SUR: top=0.00(1000)'
---

# stk dtl · tocamt sur

**Semantic key:** `stk_dtl__tocamt_sur` · **Cột vật lý:** `TOCAMT_SUR`

## Ý nghĩa nghiệp vụ

Cột TOCAMT_SUR trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOCAMT_SUR` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOCAMT_SUR`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TOCAMT_SUR
