---
semantic_key: stk_dtl__tosupp_vat
title: stk dtl · tosupp vat
display_names:
- TOSUPP_VAT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOSUPP_VAT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOSUPP_VAT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOSUPP_VAT
- 'db2:stk_dtl.TOSUPP_VAT: top=0.00(999), 180880.00(1)'
---

# stk dtl · tosupp vat

**Semantic key:** `stk_dtl__tosupp_vat` · **Cột vật lý:** `TOSUPP_VAT`

## Ý nghĩa nghiệp vụ

Cột TOSUPP_VAT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOSUPP_VAT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOSUPP_VAT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Cuối kỳ — movement: TOSUPP_VAT
