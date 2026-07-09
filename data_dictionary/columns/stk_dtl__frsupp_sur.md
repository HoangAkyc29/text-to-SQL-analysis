---
semantic_key: stk_dtl__frsupp_sur
title: stk dtl · frsupp sur
display_names:
- FRSUPP_SUR
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRSUPP_SUR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRSUPP_SUR'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRSUPP_SUR
- 'db2:stk_dtl.FRSUPP_SUR: top=0.00(1000)'
---

# stk dtl · frsupp sur

**Semantic key:** `stk_dtl__frsupp_sur` · **Cột vật lý:** `FRSUPP_SUR`

## Ý nghĩa nghiệp vụ

Cột FRSUPP_SUR trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRSUPP_SUR` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRSUPP_SUR`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRSUPP_SUR
