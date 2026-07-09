---
semantic_key: tax_code
title: tax code
display_names:
- TAX_CODE
kind: code
tables:
- ref: db1:strans
  column: TAX_CODE
  type: char
- ref: db2:asso_inf
  column: TAX_CODE
  type: char
- ref: db2:hissppr
  column: TAX_CODE
  type: char
- ref: db2:inv_iss
  column: TAX_CODE
  type: char
- ref: db2:sku_def
  column: TAX_CODE
  type: char
- ref: db2:st_order
  column: TAX_CODE
  type: char
- ref: db2:strans
  column: TAX_CODE
  type: char
- ref: db2:strans_tmp
  column: TAX_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã thuế
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.TAX_CODE: top=T5(444), NT(251), T1(222), T2(69), D0(11)'
- 'db2:asso_inf.TAX_CODE: top=NT(429), T5(293), T1(265), T2(11), N0(2)'
- 'db2:hissppr.TAX_CODE: top=T5(311), NT(240), T1(151), T2(128), N0(17)'
- 'db2:inv_iss.TAX_CODE: top=T5(28), T2(12), T1(8)'
- 'db2:sku_def.TAX_CODE: top=NT(596), T5(330), T1(68), T2(6)'
- 'db2:st_order.TAX_CODE: top=T5(825), T1(116), NT(34), T2(18), N0(7)'
- 'db2:strans.TAX_CODE: top=T5(548), T1(320), NT(90), D0(23), T2(17)'
- 'db2:strans_tmp.TAX_CODE: top=T5(436), NT(269), T1(253), T2(40), N0(2)'
---

# tax code

**Semantic key:** `tax_code` · **Cột vật lý:** `TAX_CODE`

## Ý nghĩa nghiệp vụ

Cột TAX_CODE trên ASSO_INF, HISSPPR, INV_ISS. db1:strans: top T5, D0; db2:asso_inf: top NT, T5; db2:hissppr: top T2, T5, N0; db2:sku_def: top NT, T5, T1; db2:st_order: top T5, N0; db2:strans: top T5, T1; db2:strans_tmp: top T5.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `TAX_CODE` | char | có dữ liệu |
| `db2:asso_inf` | `TAX_CODE` | char | có dữ liệu |
| `db2:hissppr` | `TAX_CODE` | char | có dữ liệu |
| `db2:inv_iss` | `TAX_CODE` | char | có dữ liệu |
| `db2:sku_def` | `TAX_CODE` | char | có dữ liệu |
| `db2:st_order` | `TAX_CODE` | char | có dữ liệu |
| `db2:strans` | `TAX_CODE` | char | có dữ liệu |
| `db2:strans_tmp` | `TAX_CODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.TAX_CODE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `T5`×19, `D0`×1

### `db2:asso_inf.TAX_CODE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `NT`×18, `T5`×2

### `db2:hissppr.TAX_CODE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `T2`×10, `T5`×8, `N0`×2

### `db2:sku_def.TAX_CODE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `NT`×15, `T5`×3, `T1`×2

### `db2:st_order.TAX_CODE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `T5`×19, `N0`×1

### `db2:strans.TAX_CODE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `T5`×19, `T1`×1

### `db2:strans_tmp.TAX_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `T5`×20

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã thuế
