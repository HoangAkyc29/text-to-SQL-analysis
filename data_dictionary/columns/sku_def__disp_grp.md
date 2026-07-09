---
semantic_key: sku_def__disp_grp
title: sku def · disp grp
display_names:
- DISP_GRP
kind: measure
tables:
- ref: db2:sku_def
  column: DISP_GRP
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột DISP_GRP
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DISP_GRP
- 'db2:sku_def.DISP_GRP: top=0(1000)'
---

# sku def · disp grp

**Semantic key:** `sku_def__disp_grp` · **Cột vật lý:** `DISP_GRP`

## Ý nghĩa nghiệp vụ

Cột DISP_GRP trên SKU_DEF. db2:sku_def: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `DISP_GRP` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.DISP_GRP`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

