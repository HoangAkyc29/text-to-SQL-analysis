---
semantic_key: stk_dtl__todeal_com
title: stk dtl · todeal com
display_names:
- TODEAL_COM
kind: measure
tables:
- ref: db2:stk_dtl
  column: TODEAL_COM
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TODEAL_COM'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TODEAL_COM
- 'db2:stk_dtl.TODEAL_COM: top=0.00(1000)'
---

# stk dtl · todeal com

**Semantic key:** `stk_dtl__todeal_com` · **Cột vật lý:** `TODEAL_COM`

## Ý nghĩa nghiệp vụ

Cột TODEAL_COM trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TODEAL_COM` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TODEAL_COM`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TODEAL_COM
