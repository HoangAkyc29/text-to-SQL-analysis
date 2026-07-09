---
semantic_key: stk_dtl__frcust_com
title: stk dtl · frcust com
display_names:
- FRCUST_COM
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCUST_COM
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCUST_COM'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRCUST_COM
- 'db2:stk_dtl.FRCUST_COM: top=0.00(1000)'
---

# stk dtl · frcust com

**Semantic key:** `stk_dtl__frcust_com` · **Cột vật lý:** `FRCUST_COM`

## Ý nghĩa nghiệp vụ

Cột FRCUST_COM trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRCUST_COM` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRCUST_COM`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRCUST_COM
