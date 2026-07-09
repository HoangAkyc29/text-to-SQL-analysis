---
semantic_key: stkname
title: stkname
display_names:
- stkname
kind: text
tables:
- ref: db2:webrpt_inventory_daily
  column: stkname
  type: nvarchar
- ref: db2:webrpt_sales_sku_daily
  column: stkname
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Tên cửa hàng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:webrpt_inventory_daily.stkname: top=Siêu thị Phan Đình Phùng(537), Siêu Thị
  Danavi (Lê Đình Lý)(231), Siêu Thị Lê Thanh Nghị(227), Kho hàng(3), Kho Marketing(1)'
- 'db2:webrpt_sales_sku_daily.stkname: top=Siêu thị Phan Đình Phùng(524), Siêu Thị
  Danavi (Lê Đình Lý)(245), Siêu Thị Lê Thanh Nghị(231)'
---

# stkname

**Semantic key:** `stkname` · **Cột vật lý:** `stkname`

## Ý nghĩa nghiệp vụ

Cột STKNAME trên WEBRPT_INVENTORY_DAILY, WEBRPT_SALES_SKU_DAILY. db2:webrpt_inventory_daily: top Siêu thị Phan Đình Phùng; db2:webrpt_sales_sku_daily: top Siêu thị Phan Đình Phùng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_inventory_daily` | `stkname` | nvarchar | có dữ liệu |
| `db2:webrpt_sales_sku_daily` | `stkname` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_inventory_daily.stkname`
- Null rate trong sample: 0%
- Distinct ≈1; top: `Siêu thị Phan Đình Phùng`×20

### `db2:webrpt_sales_sku_daily.stkname`
- Null rate trong sample: 0%
- Distinct ≈1; top: `Siêu thị Phan Đình Phùng`×20

## Ghi chú thêm

- Tên cửa hàng
