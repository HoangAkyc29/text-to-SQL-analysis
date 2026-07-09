---
semantic_key: stk_dtl__frcust_vat
title: stk dtl · frcust vat
display_names:
- FRCUST_VAT
kind: measure
tables:
- ref: db2:stk_dtl
  column: FRCUST_VAT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Đầu kỳ — movement: FRCUST_VAT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRCUST_VAT
- 'db2:stk_dtl.FRCUST_VAT: top=0.00(996), 1042666.44(1), 241778.08(1), 14607545.61(1),
  366666.30(1)'
---

# stk dtl · frcust vat

**Semantic key:** `stk_dtl__frcust_vat` · **Cột vật lý:** `FRCUST_VAT`

## Ý nghĩa nghiệp vụ

Cột FRCUST_VAT trên STK_DTL. db2:stk_dtl: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:stk_dtl` | `FRCUST_VAT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:stk_dtl.FRCUST_VAT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Đầu kỳ — movement: FRCUST_VAT
