---
semantic_key: sku_def__lbl_type
title: sku def · lbl type
display_names:
- LBL_TYPE
kind: text
tables:
- ref: db2:sku_def
  column: LBL_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột LBL_TYPE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for LBL_TYPE
- 'db2:sku_def.LBL_TYPE: top=0(165), 1(4)'
---

# sku def · lbl type

**Semantic key:** `sku_def__lbl_type` · **Cột vật lý:** `LBL_TYPE`

## Ý nghĩa nghiệp vụ

Cột LBL_TYPE trên SKU_DEF. db2:sku_def: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `LBL_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.LBL_TYPE`
- Null rate trong sample: 95%
- Distinct ≈1; top: `0`×1

## Ghi chú thêm

