---
semantic_key: sku_def__full_name
title: sku def · full name
display_names:
- FULL_NAME
kind: text
tables:
- ref: db2:sku_def
  column: FULL_NAME
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Cột FULL_NAME
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FULL_NAME
- 'db2:sku_def.FULL_NAME: top=¸o 1.10(2), PhÝch 304 800ml EL6493(1), QuÇn lãt 4-9(1),
  KÐo inox Zebra Smart 8" 993001(1), STT CGHL 170ml cao khoÎ hép(1)'
---

# sku def · full name

**Semantic key:** `sku_def__full_name` · **Cột vật lý:** `FULL_NAME`

## Ý nghĩa nghiệp vụ

Cột FULL_NAME trên SKU_DEF. db2:sku_def: top T«m rim gg 23k, ThÞt n¹c ruèc s¶ gg, Bón g¹o løt huyÕt rång 500g.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `FULL_NAME` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.FULL_NAME`
- Null rate trong sample: 0%
- Distinct ≈20; top: `T«m rim gg 23k`×1, `ThÞt n¹c ruèc s¶ gg`×1, `Bón g¹o løt huyÕt rång 500g`×1, `L¸ rong biÓn 20k`×1, `Cµ tÝm gg`×1, `Bón g¹o trén`×1, `Takoyaki 8v`×1, `Lolo thñy canh/kg`×1

## Ghi chú thêm

