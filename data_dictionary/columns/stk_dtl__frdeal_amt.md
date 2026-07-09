---
semantic_key: stk_dtl__frdeal_amt
title: stk dtl · frdeal amt
display_names:
- FRDEAL_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRDEAL_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRDEAL_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRDEAL_AMT
- 'db2:stk_dtl.FRDEAL_AMT: top=0.00(1000)'
---

# stk dtl · frdeal amt

**Semantic key:** `stk_dtl__frdeal_amt` · **Cột vật lý:** `FRDEAL_AMT`

## Ý nghĩa nghiệp vụ

Cột FRDEAL_AMT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRDEAL_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRDEAL_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRDEAL_AMT
