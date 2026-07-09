---
semantic_key: stk_dtl__frsupp_vat
title: stk dtl · frsupp vat
display_names:
- FRSUPP_VAT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRSUPP_VAT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRSUPP_VAT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRSUPP_VAT
- 'db2:stk_dtl.FRSUPP_VAT: top=0.00(958), 3284808.00(1), 5144800.00(1), 4044226.56(1),
  1938752.08(1)'
---

# stk dtl · frsupp vat

**Semantic key:** `stk_dtl__frsupp_vat` · **Cột vật lý:** `FRSUPP_VAT`

## Ý nghĩa nghiệp vụ

Cột FRSUPP_VAT trên STK_DTL. db2:stk_dtl: top 0.00, 742000.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRSUPP_VAT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRSUPP_VAT`
- Null rate trong sample: 0%
- Distinct ≈2; top: `0.00`×19, `742000.00`×1

## Ghi chú thêm

- Đầu kỳ — movement: FRSUPP_VAT
