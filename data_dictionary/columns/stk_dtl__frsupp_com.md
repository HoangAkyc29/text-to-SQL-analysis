---
semantic_key: stk_dtl__frsupp_com
title: stk dtl · frsupp com
display_names:
- FRSUPP_COM
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRSUPP_COM
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRSUPP_COM'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRSUPP_COM
- 'db2:stk_dtl.FRSUPP_COM: top=0.00(1000)'
---

# stk dtl · frsupp com

**Semantic key:** `stk_dtl__frsupp_com` · **Cột vật lý:** `FRSUPP_COM`

## Ý nghĩa nghiệp vụ

Cột FRSUPP_COM trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRSUPP_COM` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRSUPP_COM`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRSUPP_COM
