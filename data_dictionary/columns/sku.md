---
semantic_key: sku
title: sku
display_names:
- SKU
kind: flag
tables:
- ref: db1:strans
  column: SKU
  type: bit
- ref: db2:assolst
  column: SKU
  type: bit
- ref: db2:sku_def
  column: SKU
  type: bit
- ref: db2:strans
  column: SKU
  type: bit
- ref: db2:strans_tmp
  column: SKU
  type: bit
- ref: db2:suspend
  column: SKU
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột SKU
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.SKU: top=True(1000)'
- 'db2:assolst.SKU: top=False(1000)'
- 'db2:sku_def.SKU: top=True(1000)'
- 'db2:strans.SKU: top=True(1000)'
- 'db2:strans_tmp.SKU: top=True(1000)'
- 'db2:suspend.SKU: top=True(1000)'
---

# sku

**Semantic key:** `sku` · **Cột vật lý:** `SKU`

## Ý nghĩa nghiệp vụ

Cột SKU trên ASSOLST, SKU_DEF, STRANS. db1:strans: top True; db2:assolst: top False; db2:sku_def: top True; db2:strans: top True; db2:strans_tmp: top True; db2:suspend: top True.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `SKU` | bit | có dữ liệu |
| `db2:assolst` | `SKU` | bit | có dữ liệu |
| `db2:sku_def` | `SKU` | bit | có dữ liệu |
| `db2:strans` | `SKU` | bit | có dữ liệu |
| `db2:strans_tmp` | `SKU` | bit | có dữ liệu |
| `db2:suspend` | `SKU` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.SKU`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:assolst.SKU`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

### `db2:sku_def.SKU`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:strans.SKU`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:strans_tmp.SKU`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

### `db2:suspend.SKU`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

## Ghi chú thêm

