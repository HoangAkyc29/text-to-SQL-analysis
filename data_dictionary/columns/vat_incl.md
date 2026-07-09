---
semantic_key: vat_incl
title: vat incl
display_names:
- VAT_INCL
kind: flag
tables:
- ref: db1:strans
  column: VAT_INCL
  type: bit
- ref: db2:plu
  column: VAT_INCL
  type: bit
- ref: db2:st_order
  column: VAT_INCL
  type: bit
- ref: db2:strans
  column: VAT_INCL
  type: bit
- ref: db2:strans_tmp
  column: VAT_INCL
  type: bit
- ref: db2:suspend
  column: VAT_INCL
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Giá đã gồm VAT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.VAT_INCL: top=True(786), False(214)'
- 'db2:plu.VAT_INCL: top=False(1000)'
- 'db2:st_order.VAT_INCL: top=False(1000)'
- 'db2:strans.VAT_INCL: top=True(882), False(118)'
- 'db2:strans_tmp.VAT_INCL: top=True(1000)'
- 'db2:suspend.VAT_INCL: top=False(1000)'
---

# vat incl

**Semantic key:** `vat_incl` · **Cột vật lý:** `VAT_INCL`

## Ý nghĩa nghiệp vụ

Cột VAT_INCL trên PLU, STRANS, STRANS_TMP. db1:strans: top False, True; db2:plu: top False; db2:st_order: top False; db2:strans: top False, True; db2:strans_tmp: top True; db2:suspend: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `VAT_INCL` | bit | có dữ liệu |
| `db2:plu` | `VAT_INCL` | bit | có dữ liệu |
| `db2:st_order` | `VAT_INCL` | bit | có dữ liệu |
| `db2:strans` | `VAT_INCL` | bit | có dữ liệu |
| `db2:strans_tmp` | `VAT_INCL` | bit | có dữ liệu |
| `db2:suspend` | `VAT_INCL` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.VAT_INCL`
- Null rate trong sample: 0%
- Distinct ≈2; top: `False`×16, `True`×4

### `db2:plu.VAT_INCL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:st_order.VAT_INCL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:strans.VAT_INCL`
- Null rate trong sample: 0%
- Distinct ≈2; top: `False`×16, `True`×4

### `db2:strans_tmp.VAT_INCL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:suspend.VAT_INCL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

- Giá đã gồm VAT
