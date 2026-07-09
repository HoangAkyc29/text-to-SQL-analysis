---
semantic_key: stk_dtl__frdeal_vat
title: stk dtl · frdeal vat
display_names:
- FRDEAL_VAT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRDEAL_VAT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRDEAL_VAT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRDEAL_VAT
- 'db2:stk_dtl.FRDEAL_VAT: top=0.00(1000)'
---

# stk dtl · frdeal vat

**Semantic key:** `stk_dtl__frdeal_vat` · **Cột vật lý:** `FRDEAL_VAT`

## Ý nghĩa nghiệp vụ

Cột FRDEAL_VAT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRDEAL_VAT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRDEAL_VAT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRDEAL_VAT
