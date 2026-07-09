---
semantic_key: sku_def__bon_mark
title: sku def · bon mark
display_names:
- BON_MARK
kind: measure
tables:
- ref: db2:sku_def
  column: BON_MARK
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột BON_MARK
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BON_MARK
- 'db2:sku_def.BON_MARK: top=0.00(1000)'
---

# sku def · bon mark

**Semantic key:** `sku_def__bon_mark` · **Cột vật lý:** `BON_MARK`

## Ý nghĩa nghiệp vụ

Cột BON_MARK trên SKU_DEF. db2:sku_def: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `BON_MARK` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.BON_MARK`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

