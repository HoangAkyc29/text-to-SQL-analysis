---
semantic_key: sku_def__abc
title: sku def · abc
display_names:
- ABC
kind: text
tables:
- ref: db2:sku_def
  column: ABC
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Cột ABC
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for ABC
- 'db2:sku_def.ABC: top=B(32), A(2)'
---

# sku def · abc

**Semantic key:** `sku_def__abc` · **Cột vật lý:** `ABC`

## Ý nghĩa nghiệp vụ

Cột ABC trên SKU_DEF. db2:sku_def: top B.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `ABC` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.ABC`
- Null rate trong sample: 95%
- Distinct ≈1; top: `B`×1

## Ghi chú thêm

