---
semantic_key: mbc
title: mbc
display_names:
- MBC
kind: flag
tables:
- ref: db1:strans
  column: MBC
  type: bit
- ref: db2:assolst
  column: MBC
  type: bit
- ref: db2:sku_def
  column: MBC
  type: bit
- ref: db2:strans
  column: MBC
  type: bit
- ref: db2:strans_tmp
  column: MBC
  type: bit
- ref: db2:suspend
  column: MBC
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột MBC
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.MBC: top=False(1000)'
- 'db2:assolst.MBC: top=False(1000)'
- 'db2:sku_def.MBC: top=False(1000)'
- 'db2:strans.MBC: top=False(1000)'
- 'db2:strans_tmp.MBC: top=False(1000)'
- 'db2:suspend.MBC: top=False(1000)'
---

# mbc

**Semantic key:** `mbc` · **Cột vật lý:** `MBC`

## Ý nghĩa nghiệp vụ

Cột MBC trên ASSOLST, SKU_DEF, STRANS. db1:strans: top False; db2:assolst: top False; db2:sku_def: top False; db2:strans: top False; db2:strans_tmp: top False; db2:suspend: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `MBC` | bit | có dữ liệu |
| `db2:assolst` | `MBC` | bit | có dữ liệu |
| `db2:sku_def` | `MBC` | bit | có dữ liệu |
| `db2:strans` | `MBC` | bit | có dữ liệu |
| `db2:strans_tmp` | `MBC` | bit | có dữ liệu |
| `db2:suspend` | `MBC` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.MBC`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:assolst.MBC`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:sku_def.MBC`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:strans.MBC`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:strans_tmp.MBC`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:suspend.MBC`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

