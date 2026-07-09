---
semantic_key: grpname
title: grpname
display_names:
- grpname
kind: text
tables:
- ref: db2:webrpt_inventory_daily
  column: grpname
  type: nvarchar
- ref: db2:webrpt_sales_sku_daily
  column: grpname
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Tên nhóm hàng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:webrpt_inventory_daily.grpname: top=Đồ gia dụng các loại(143), Bánh kẹo các
  loại(124), Thời trang nữ(120), Thực phẩm tươi các loại(98), Các sản phẩm sơ chế(88)'
- 'db2:webrpt_sales_sku_daily.grpname: top=Thực phẩm tươi các loại(162), Bánh kẹo
  các loại(147), Đường, sữa,sữa chua,kem các loại(87), Thức ăn nhanh các loại(72),
  Đồ khô các loại(65)'
---

# grpname

**Semantic key:** `grpname` · **Cột vật lý:** `grpname`

## Ý nghĩa nghiệp vụ

Cột GRPNAME trên WEBRPT_INVENTORY_DAILY, WEBRPT_SALES_SKU_DAILY. db2:webrpt_inventory_daily: top Các sản phẩm sơ chế, Thực phẩm tươi các loại, Đồ uống các loại; db2:webrpt_sales_sku_daily: top Các sản phẩm sơ chế, Thức ăn nhanh các loại, Đồ khô các loại.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_inventory_daily` | `grpname` | nvarchar | có dữ liệu |
| `db2:webrpt_sales_sku_daily` | `grpname` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_inventory_daily.grpname`
- Null rate trong sample: 0%
- Distinct ≈6; top: `Các sản phẩm sơ chế`×10, `Thực phẩm tươi các loại`×4, `Đồ uống các loại`×2, `Chất tẩy rửa các loại`×2, `Mỹ phẩm dưỡng da, chăm sóc da`×1, `Đồ gia dụng các loại`×1

### `db2:webrpt_sales_sku_daily.grpname`
- Null rate trong sample: 0%
- Distinct ≈7; top: `Các sản phẩm sơ chế`×7, `Thức ăn nhanh các loại`×7, `Đồ khô các loại`×2, `Ngũ cốc các loại`×1, `Mỹ phẩm dưỡng da, chăm sóc da`×1, `Đồ uống các loại`×1, `Thực phẩm tươi các loại`×1

## Ghi chú thêm

- Tên nhóm hàng
