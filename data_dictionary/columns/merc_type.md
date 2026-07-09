---
semantic_key: merc_type
title: merc type
display_names:
- MERC_TYPE
kind: code
tables:
- ref: db1:strans
  column: MERC_TYPE
  type: char
- ref: db2:asso_inf
  column: MERC_TYPE
  type: char
- ref: db2:plu
  column: MERC_TYPE
  type: char
- ref: db2:sku_def
  column: MERC_TYPE
  type: char
- ref: db2:strans
  column: MERC_TYPE
  type: char
- ref: db2:strans_tmp
  column: MERC_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại hàng hóa
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.MERC_TYPE: top=01(1000)'
- 'db2:asso_inf.MERC_TYPE: top=01(723), 02(277)'
- 'db2:plu.MERC_TYPE: top=02(987), 03(7), 01(6)'
- 'db2:sku_def.MERC_TYPE: top=01(970), 02(30)'
- 'db2:strans.MERC_TYPE: top=01(1000)'
- 'db2:strans_tmp.MERC_TYPE: top=01(1000)'
---

# merc type

**Semantic key:** `merc_type` · **Cột vật lý:** `MERC_TYPE`

## Ý nghĩa nghiệp vụ

Cột MERC_TYPE trên ASSO_INF, PLU, SKU_DEF. db1:strans: top 01; db2:asso_inf: top 01, 02; db2:plu: top 02; db2:sku_def: top 01, 02; db2:strans: top 01; db2:strans_tmp: top 01.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `MERC_TYPE` | char | có dữ liệu |
| `db2:asso_inf` | `MERC_TYPE` | char | có dữ liệu |
| `db2:plu` | `MERC_TYPE` | char | có dữ liệu |
| `db2:sku_def` | `MERC_TYPE` | char | có dữ liệu |
| `db2:strans` | `MERC_TYPE` | char | có dữ liệu |
| `db2:strans_tmp` | `MERC_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.MERC_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

### `db2:asso_inf.MERC_TYPE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `01`×17, `02`×3

### `db2:plu.MERC_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `02`×20

### `db2:sku_def.MERC_TYPE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `01`×19, `02`×1

### `db2:strans.MERC_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

### `db2:strans_tmp.MERC_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

## Ghi chú thêm

- Loại hàng hóa
