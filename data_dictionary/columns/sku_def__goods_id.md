---
semantic_key: sku_def__goods_id
title: sku def · goods id
display_names:
- GOODS_ID
kind: identifier
tables:
- ref: db2:sku_def
  column: GOODS_ID
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Cột GOODS_ID
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for GOODS_ID
- 'db2:sku_def.GOODS_ID: top=02128044(1), 04004222(1), 00010614(1), 06002066(1), 02129180(1)'
---

# sku def · goods id

**Semantic key:** `sku_def__goods_id` · **Cột vật lý:** `GOODS_ID`

## Ý nghĩa nghiệp vụ

Cột GOODS_ID trên SKU_DEF. db2:sku_def: top 00000001, 00000002, 00000003.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `GOODS_ID` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.GOODS_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `00000001`×1, `00000002`×1, `00000003`×1, `00000004`×1, `00000005`×1, `00000006`×1, `00000007`×1, `00000008`×1

## Ghi chú thêm

