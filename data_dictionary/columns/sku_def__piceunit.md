---
semantic_key: sku_def__piceunit
title: sku def · piceunit
display_names:
- PICEUNIT
kind: text
tables:
- ref: db2:sku_def
  column: PICEUNIT
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột PICEUNIT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for PICEUNIT
- 'db2:sku_def.PICEUNIT: top=CAI(542), HOP(91), KHA(80), GOI(78), CHA(56)'
---

# sku def · piceunit

**Semantic key:** `sku_def__piceunit` · **Cột vật lý:** `PICEUNIT`

## Ý nghĩa nghiệp vụ

Cột PICEUNIT trên SKU_DEF. db2:sku_def: top CAI, KHA, BAO.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `PICEUNIT` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.PICEUNIT`
- Null rate trong sample: 0%
- Distinct ≈5; top: `CAI`×12, `KHA`×5, `BAO`×1, `HOP`×1, `KG`×1

## Ghi chú thêm

