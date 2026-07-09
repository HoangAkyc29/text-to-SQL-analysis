---
semantic_key: stk_dtl__frsupp_dis
title: stk dtl · frsupp dis
display_names:
- FRSUPP_DIS
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRSUPP_DIS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRSUPP_DIS'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRSUPP_DIS
- 'db2:stk_dtl.FRSUPP_DIS: top=0.00(991), 1015920.00(1), 388800.00(1), 11638850.40(1),
  3681065.76(1)'
---

# stk dtl · frsupp dis

**Semantic key:** `stk_dtl__frsupp_dis` · **Cột vật lý:** `FRSUPP_DIS`

## Ý nghĩa nghiệp vụ

Cột FRSUPP_DIS trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRSUPP_DIS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRSUPP_DIS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRSUPP_DIS
