---
semantic_key: stk_dtl__tosupp_dis
title: stk dtl · tosupp dis
display_names:
- TOSUPP_DIS
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOSUPP_DIS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOSUPP_DIS'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOSUPP_DIS
- 'db2:stk_dtl.TOSUPP_DIS: top=0.00(1000)'
---

# stk dtl · tosupp dis

**Semantic key:** `stk_dtl__tosupp_dis` · **Cột vật lý:** `TOSUPP_DIS`

## Ý nghĩa nghiệp vụ

Cột TOSUPP_DIS trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOSUPP_DIS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOSUPP_DIS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TOSUPP_DIS
