---
semantic_key: stk_dtl__tosupp_sur
title: stk dtl · tosupp sur
display_names:
- TOSUPP_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOSUPP_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOSUPP_SUR'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOSUPP_SUR
- 'db2:stk_dtl.TOSUPP_SUR: top=0.00(1000)'
---

# stk dtl · tosupp sur

**Semantic key:** `stk_dtl__tosupp_sur` · **Cột vật lý:** `TOSUPP_SUR`

## Ý nghĩa nghiệp vụ

Cột TOSUPP_SUR trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOSUPP_SUR` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOSUPP_SUR`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TOSUPP_SUR
