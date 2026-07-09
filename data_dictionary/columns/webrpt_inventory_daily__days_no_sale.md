---
semantic_key: webrpt_inventory_daily__days_no_sale
title: webrpt inventory daily · days no sale
display_names:
- days_no_sale
kind: measure
tables:
- ref: db2:webrpt_inventory_daily
  column: days_no_sale
  type: int
join_with: []
related_semantic_keys: []
facts:
- Số ngày không bán
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for days_no_sale
- 'db2:webrpt_inventory_daily.days_no_sale: min=41.0 max=909.0'
---

# webrpt inventory daily · days no sale

**Semantic key:** `webrpt_inventory_daily__days_no_sale` · **Cột vật lý:** `days_no_sale`

## Ý nghĩa nghiệp vụ

Cột DAYS_NO_SALE trên WEBRPT_INVENTORY_DAILY. db2:webrpt_inventory_daily: 113.0…800.0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_inventory_daily` | `days_no_sale` | int | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_inventory_daily.days_no_sale`
- Null rate trong sample: 55%
- Numeric range: 113.0 … 800.0
- Ví dụ: 136, 289, 113, 462, 711

## Ghi chú thêm

- Số ngày không bán
