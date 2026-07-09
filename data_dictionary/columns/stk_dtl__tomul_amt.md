---
semantic_key: stk_dtl__tomul_amt
title: stk dtl · tomul amt
display_names:
- TOMUL_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOMUL_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOMUL_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOMUL_AMT
- 'db2:stk_dtl.TOMUL_AMT: top=0.00(998), 27849739.80(1), 18327274.56(1)'
---

# stk dtl · tomul amt

**Semantic key:** `stk_dtl__tomul_amt` · **Cột vật lý:** `TOMUL_AMT`

## Ý nghĩa nghiệp vụ

Cột TOMUL_AMT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOMUL_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOMUL_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TOMUL_AMT
