---
semantic_key: stk_dtl__todeal_vat
title: stk dtl · todeal vat
display_names:
- TODEAL_VAT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TODEAL_VAT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TODEAL_VAT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TODEAL_VAT
- 'db2:stk_dtl.TODEAL_VAT: top=0.00(1000)'
---

# stk dtl · todeal vat

**Semantic key:** `stk_dtl__todeal_vat` · **Cột vật lý:** `TODEAL_VAT`

## Ý nghĩa nghiệp vụ

Cột TODEAL_VAT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TODEAL_VAT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TODEAL_VAT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TODEAL_VAT
