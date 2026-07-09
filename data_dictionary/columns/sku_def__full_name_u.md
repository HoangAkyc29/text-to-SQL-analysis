---
semantic_key: sku_def__full_name_u
title: sku def · full name u
display_names:
- FULL_NAME_U
kind: text
tables:
- ref: db2:sku_def
  column: FULL_NAME_U
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Cột FULL_NAME_U
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FULL_NAME_U
- 'db2:sku_def.FULL_NAME_U: top=áo 1.10(2), Phích 304 800ml EL6493(1), Quần lót 4-9(1),
  Kéo inox Zebra Smart 8" 993001(1), STT CGHL 170ml cao khoẻ hộp(1)'
---

# sku def · full name u

**Semantic key:** `sku_def__full_name_u` · **Cột vật lý:** `FULL_NAME_U`

## Ý nghĩa nghiệp vụ

Cột FULL_NAME_U trên SKU_DEF. db2:sku_def: top Tôm rim gg 23k, Thịt nạc ruốc sả gg, Bún gạo lứt huyết rồng 500g.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `FULL_NAME_U` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.FULL_NAME_U`
- Null rate trong sample: 0%
- Distinct ≈20; top: `Tôm rim gg 23k`×1, `Thịt nạc ruốc sả gg`×1, `Bún gạo lứt huyết rồng 500g`×1, `Lá rong biển 20k`×1, `Cà tím gg`×1, `Bún gạo trộn`×1, `Takoyaki 8v`×1, `Lolo thủy canh/kg`×1

## Ghi chú thêm

