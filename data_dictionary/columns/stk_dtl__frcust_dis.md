---
semantic_key: stk_dtl__frcust_dis
title: stk dtl · frcust dis
display_names:
- FRCUST_DIS
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCUST_DIS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCUST_DIS'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRCUST_DIS
- 'db2:stk_dtl.FRCUST_DIS: top=0.00(1000)'
---

# stk dtl · frcust dis

**Semantic key:** `stk_dtl__frcust_dis` · **Cột vật lý:** `FRCUST_DIS`

## Ý nghĩa nghiệp vụ

Cột FRCUST_DIS trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRCUST_DIS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRCUST_DIS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRCUST_DIS
