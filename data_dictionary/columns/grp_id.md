---
semantic_key: grp_id
title: grp id
display_names:
- grp_id
- GRP_ID
kind: identifier
tables:
- ref: db2:customer
  column: GRP_ID
  type: char
- ref: db2:partner
  column: GRP_ID
  type: char
- ref: db2:sku_def
  column: GRP_ID
  type: varchar
- ref: db2:supplier
  column: GRP_ID
  type: char
- ref: db2:webrpt_inventory_daily
  column: grp_id
  type: varchar
- ref: db2:webrpt_sales_sku_daily
  column: grp_id
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Mã nhóm hàng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:customer.GRP_ID: top=3001(996), 3005(1)'
- 'db2:partner.GRP_ID: top=5001(444), 0000(218), 4001(10), 001(3), 3001(1)'
- 'db2:sku_def.GRP_ID: top=080001(197), 020000(117), 080004(80), 030000(69), 040200(56)'
- 'db2:supplier.GRP_ID: top=5001(463), 0000(212)'
- 'db2:webrpt_inventory_daily.grp_id: top=020000(143), 060101(124), 080001(120), 030000(98),
  030100(88)'
- 'db2:webrpt_sales_sku_daily.grp_id: top=030000(162), 060101(147), 060106(87), 030310(72),
  030302(65)'
---

# grp id

**Semantic key:** `grp_id` · **Cột vật lý:** `grp_id`, `GRP_ID`

## Ý nghĩa nghiệp vụ

Cột GRP_ID trên CUSTOMER, PARTNER, SKU_DEF. db2:customer: top 3001; db2:partner: top 5001; db2:sku_def: top 080001, 030100, 030000; db2:supplier: top 5001; db2:webrpt_inventory_daily: top 030100, 030000, 060102; db2:webrpt_sales_sku_daily: top 030100, 030310, 030302.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `GRP_ID` | char | có dữ liệu |
| `db2:partner` | `GRP_ID` | char | có dữ liệu |
| `db2:sku_def` | `GRP_ID` | varchar | có dữ liệu |
| `db2:supplier` | `GRP_ID` | char | có dữ liệu |
| `db2:webrpt_inventory_daily` | `grp_id` | varchar | có dữ liệu |
| `db2:webrpt_sales_sku_daily` | `grp_id` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:customer.GRP_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `3001`×20

### `db2:partner.GRP_ID`
- Null rate trong sample: 95%
- Distinct ≈1; top: `5001`×1

### `db2:sku_def.GRP_ID`
- Null rate trong sample: 0%
- Distinct ≈4; top: `080001`×12, `030100`×5, `030000`×2, `030301`×1

### `db2:supplier.GRP_ID`
- Null rate trong sample: 85%
- Distinct ≈1; top: `5001`×3

### `db2:webrpt_inventory_daily.grp_id`
- Null rate trong sample: 0%
- Distinct ≈6; top: `030100`×10, `030000`×4, `060102`×2, `010100`×2, `010000`×1, `020000`×1

### `db2:webrpt_sales_sku_daily.grp_id`
- Null rate trong sample: 0%
- Distinct ≈7; top: `030100`×7, `030310`×7, `030302`×2, `030301`×1, `010000`×1, `060102`×1, `030000`×1

## Ghi chú thêm

- Mã nhóm hàng
