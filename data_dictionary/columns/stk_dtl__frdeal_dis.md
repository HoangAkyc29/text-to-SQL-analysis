---
semantic_key: stk_dtl__frdeal_dis
title: stk dtl · frdeal dis
display_names:
- FRDEAL_DIS
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRDEAL_DIS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRDEAL_DIS'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRDEAL_DIS
- 'db2:stk_dtl.FRDEAL_DIS: top=0.00(1000)'
---

# stk dtl · frdeal dis

**Semantic key:** `stk_dtl__frdeal_dis` · **Cột vật lý:** `FRDEAL_DIS`

## Ý nghĩa nghiệp vụ

Cột FRDEAL_DIS trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRDEAL_DIS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRDEAL_DIS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRDEAL_DIS
