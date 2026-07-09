---
semantic_key: stk_dtl__tocust_vat
title: stk dtl · tocust vat
display_names:
- TOCUST_VAT
kind: measure
tables:
- ref: db2:stk_dtl
  column: TOCUST_VAT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Cuối kỳ — movement: TOCUST_VAT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TOCUST_VAT
- 'db2:stk_dtl.TOCUST_VAT: top=0.00(907), 7488151.66(1), 280563.24(1), 5751666.27(1),
  1295272.69(1)'
---

# stk dtl · tocust vat

**Semantic key:** `stk_dtl__tocust_vat` · **Cột vật lý:** `TOCUST_VAT`

## Ý nghĩa nghiệp vụ

Cột TOCUST_VAT trên STK_DTL. db2:stk_dtl: top 0.00, 872665.76, 4152297.24.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `TOCUST_VAT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.TOCUST_VAT`
- Null rate trong sample: 0%
- Distinct ≈4; top: `0.00`×17, `872665.76`×1, `4152297.24`×1, `31211365.42`×1

## Ghi chú thêm

- Cuối kỳ — movement: TOCUST_VAT
