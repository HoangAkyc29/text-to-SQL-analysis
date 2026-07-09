---
semantic_key: sku_def__grp_name
title: sku def · grp name
display_names:
- GRP_NAME
kind: text
tables:
- ref: db2:sku_def
  column: GRP_NAME
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Cột GRP_NAME
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for GRP_NAME
- 'db2:sku_def.GRP_NAME: top=Thêi trang n÷(197), §å gia dông c¸c lo¹i(117), Phô kiÖn
  nÞt, vÝ, giá, cµ v¹t...(80), Thùc phÈm t­¬i c¸c lo¹i(69), §å ch¬i trÎ em(56)'
---

# sku def · grp name

**Semantic key:** `sku_def__grp_name` · **Cột vật lý:** `GRP_NAME`

## Ý nghĩa nghiệp vụ

Cột GRP_NAME trên SKU_DEF. db2:sku_def: top Thêi trang n÷, C¸c s¶n phÈm s¬ chÕ, Thùc phÈm t­¬i c¸c lo¹i.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `GRP_NAME` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.GRP_NAME`
- Null rate trong sample: 0%
- Distinct ≈4; top: `Thêi trang n÷`×12, `C¸c s¶n phÈm s¬ chÕ`×5, `Thùc phÈm t­¬i c¸c lo¹i`×2, `Ngò cèc c¸c lo¹i`×1

## Ghi chú thêm

