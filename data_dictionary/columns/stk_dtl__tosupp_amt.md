---
semantic_key: stk_dtl__tosupp_amt
title: stk dtl · tosupp amt
display_names:
- TOSUPP_AMT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOSUPP_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOSUPP_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOSUPP_AMT
- 'db2:stk_dtl.TOSUPP_AMT: top=0.00(999), 1808800.00(1)'
---

# stk dtl · tosupp amt

**Semantic key:** `stk_dtl__tosupp_amt` · **Cột vật lý:** `TOSUPP_AMT`

## Ý nghĩa nghiệp vụ

Cột TOSUPP_AMT trên STK_DTL. db2:stk_dtl: top 0.00, 19161600.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOSUPP_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOSUPP_AMT`
- Null rate trong sample: 0%
- Distinct ≈2; top: `0.00`×19, `19161600.00`×1

## Ghi chú thêm

- Cuối kỳ — movement: TOSUPP_AMT
