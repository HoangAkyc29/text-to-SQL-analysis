---
semantic_key: stk_dtl__frdeal_com
title: stk dtl · frdeal com
display_names:
- FRDEAL_COM
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRDEAL_COM
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRDEAL_COM'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRDEAL_COM
- 'db2:stk_dtl.FRDEAL_COM: top=0.00(1000)'
---

# stk dtl · frdeal com

**Semantic key:** `stk_dtl__frdeal_com` · **Cột vật lý:** `FRDEAL_COM`

## Ý nghĩa nghiệp vụ

Cột FRDEAL_COM trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRDEAL_COM` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRDEAL_COM`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRDEAL_COM
