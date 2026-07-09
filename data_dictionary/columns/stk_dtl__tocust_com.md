---
semantic_key: stk_dtl__tocust_com
title: stk dtl · tocust com
display_names:
- TOCUST_COM
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCUST_COM
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCUST_COM'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOCUST_COM
- 'db2:stk_dtl.TOCUST_COM: top=0.00(1000)'
---

# stk dtl · tocust com

**Semantic key:** `stk_dtl__tocust_com` · **Cột vật lý:** `TOCUST_COM`

## Ý nghĩa nghiệp vụ

Cột TOCUST_COM trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOCUST_COM` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOCUST_COM`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TOCUST_COM
