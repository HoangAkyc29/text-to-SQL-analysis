---
semantic_key: stk_dtl__frdeal_sur
title: stk dtl · frdeal sur
display_names:
- FRDEAL_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRDEAL_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRDEAL_SUR'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRDEAL_SUR
- 'db2:stk_dtl.FRDEAL_SUR: top=0.00(1000)'
---

# stk dtl · frdeal sur

**Semantic key:** `stk_dtl__frdeal_sur` · **Cột vật lý:** `FRDEAL_SUR`

## Ý nghĩa nghiệp vụ

Cột FRDEAL_SUR trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRDEAL_SUR` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRDEAL_SUR`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRDEAL_SUR
