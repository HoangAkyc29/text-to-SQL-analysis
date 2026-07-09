---
semantic_key: skucode
title: skucode
display_names:
- skucode
kind: text
tables:
- ref: db2:webrpt_inventory_daily
  column: skucode
  type: varchar
- ref: db2:webrpt_sales_sku_daily
  column: skucode
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Mã SKU hiển thị
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:webrpt_inventory_daily.skucode: top=00028441(2), 00019693(2), 00023578(2),
  00015324(2), 03126736(2)'
- 'db2:webrpt_sales_sku_daily.skucode: top=03127011(3), 03101497(3), 03101704(3),
  00026214(3), 06126677(3)'
---

# skucode

**Semantic key:** `skucode` · **Cột vật lý:** `skucode`

## Ý nghĩa nghiệp vụ

Cột SKUCODE trên WEBRPT_INVENTORY_DAILY, WEBRPT_SALES_SKU_DAILY. db2:webrpt_inventory_daily: top 00000001, 00000002, 00000004; db2:webrpt_sales_sku_daily: top 00000003, 00000111, 00000123.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_inventory_daily` | `skucode` | varchar | có dữ liệu |
| `db2:webrpt_sales_sku_daily` | `skucode` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_inventory_daily.skucode`
- Null rate trong sample: 0%
- Distinct ≈20; top: `00000001`×1, `00000002`×1, `00000004`×1, `00003536`×1, `00000007`×1, `00000008`×1, `00000073`×1, `00000078`×1

### `db2:webrpt_sales_sku_daily.skucode`
- Null rate trong sample: 0%
- Distinct ≈20; top: `00000003`×1, `00000111`×1, `00000123`×1, `00000127`×1, `00000548`×1, `00000596`×1, `00000608`×1, `00000613`×1

## Ghi chú thêm

- Mã SKU hiển thị
