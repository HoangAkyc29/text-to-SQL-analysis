---
semantic_key: item_type
title: item type
display_names:
- ITEM_TYPE
kind: code
tables:
- ref: db2:asso_inf
  column: ITEM_TYPE
  type: char
- ref: db2:sku_def
  column: ITEM_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại dòng hàng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:asso_inf.ITEM_TYPE: top=01(991), 09(9)'
- 'db2:sku_def.ITEM_TYPE: top=01(996), 09(4)'
---

# item type

**Semantic key:** `item_type` · **Cột vật lý:** `ITEM_TYPE`

## Ý nghĩa nghiệp vụ

Cột ITEM_TYPE trên ASSO_INF, SKU_DEF. db2:asso_inf: top 01; db2:sku_def: top 01.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:asso_inf` | `ITEM_TYPE` | char | có dữ liệu |
| `db2:sku_def` | `ITEM_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:asso_inf.ITEM_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

### `db2:sku_def.ITEM_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

## Ghi chú thêm

- Loại dòng hàng
