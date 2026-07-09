---
semantic_key: skuname
title: skuname
display_names:
- skuname
kind: text
tables:
- ref: db2:webrpt_inventory_daily
  column: skuname
  type: nvarchar
- ref: db2:webrpt_sales_sku_daily
  column: skuname
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Tên sản phẩm
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:webrpt_inventory_daily.skuname: top=Đầu nành sấy giòn Tili 200g(2), áo 2++4**(2),
  190625 áo 2.8(2), Bộ nữ 01++19(2), Dấm táo CJ 500ml(2)'
- 'db2:webrpt_sales_sku_daily.skuname: top=Cải ngọt Trà quế 500g(3), Thịt heo 2 lát
  150g Vissan(3), Cá hộp 3 cô gái 155g(3), Dầu hướng dương Nga Faricook 1 lít(3),
  Sữa chua ăn nha đam TH Truemilk 100g lốc 4(3)'
---

# skuname

**Semantic key:** `skuname` · **Cột vật lý:** `skuname`

## Ý nghĩa nghiệp vụ

Cột SKUNAME trên WEBRPT_INVENTORY_DAILY, WEBRPT_SALES_SKU_DAILY. db2:webrpt_inventory_daily: top Tôm rim gg 23k, Thịt nạc ruốc sả gg, Lá rong biển 20k; db2:webrpt_sales_sku_daily: top Bún gạo lứt huyết rồng 500g, Khăn ướt trẻ em  Bobby care 100t, Chè thanh nhiệt.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_inventory_daily` | `skuname` | nvarchar | có dữ liệu |
| `db2:webrpt_sales_sku_daily` | `skuname` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_inventory_daily.skuname`
- Null rate trong sample: 0%
- Distinct ≈20; top: `Tôm rim gg 23k`×1, `Thịt nạc ruốc sả gg`×1, `Lá rong biển 20k`×1, `Bún gạo trộn`×1, `Takoyaki 8v`×1, `Lolo thủy canh/kg`×1, `Mực cơm khay 20k`×1, `7 up Free Fiber 320ml lon`×1

### `db2:webrpt_sales_sku_daily.skuname`
- Null rate trong sample: 0%
- Distinct ≈20; top: `Bún gạo lứt huyết rồng 500g`×1, `Khăn ướt trẻ em  Bobby care 100t`×1, `Chè thanh nhiệt`×1, `Set chè thanh nhiệt`×1, `Sushi lươn , bơ , trứng`×1, `Chả cá thát lát có gia vị/kg`×1, `Muối tôm Tây Ninh 110g`×1, `Muối  ớt Tây Ninh 110g`×1

## Ghi chú thêm

- Tên sản phẩm
