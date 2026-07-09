---
semantic_key: stk_dtl__todeal_dis
title: stk dtl · todeal dis
display_names:
- TODEAL_DIS
kind: measure
tables:
- ref: db2:stk_dtl
  column: TODEAL_DIS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TODEAL_DIS'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TODEAL_DIS
- 'db2:stk_dtl.TODEAL_DIS: top=0.00(1000)'
---

# stk dtl · todeal dis

**Semantic key:** `stk_dtl__todeal_dis` · **Cột vật lý:** `TODEAL_DIS`

## Ý nghĩa nghiệp vụ

Cột TODEAL_DIS trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TODEAL_DIS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TODEAL_DIS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TODEAL_DIS
