---
semantic_key: stk_dtl__tocust_dis
title: stk dtl · tocust dis
display_names:
- TOCUST_DIS
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCUST_DIS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCUST_DIS'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOCUST_DIS
- 'db2:stk_dtl.TOCUST_DIS: top=0.00(999), 68000.00(1)'
---

# stk dtl · tocust dis

**Semantic key:** `stk_dtl__tocust_dis` · **Cột vật lý:** `TOCUST_DIS`

## Ý nghĩa nghiệp vụ

Cột TOCUST_DIS trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOCUST_DIS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOCUST_DIS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TOCUST_DIS
