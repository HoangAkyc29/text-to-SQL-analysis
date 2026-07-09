---
semantic_key: webrpt_inventory_daily__value_onhand
title: webrpt inventory daily · value onhand
display_names:
- value_onhand
kind: measure
tables:
- ref: db2:webrpt_inventory_daily
  column: value_onhand
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Giá trị tồn
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for value_onhand
- 'db2:webrpt_inventory_daily.value_onhand: top=0.00(554), 120000.00(3), 105000.00(3),
  75000.00(3), 119000.00(2)'
---

# webrpt inventory daily · value onhand

**Semantic key:** `webrpt_inventory_daily__value_onhand` · **Cột vật lý:** `value_onhand`

## Ý nghĩa nghiệp vụ

Cột VALUE_ONHAND trên WEBRPT_INVENTORY_DAILY. db2:webrpt_inventory_daily: top 0.00, 144.00, 226.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_inventory_daily` | `value_onhand` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_inventory_daily.value_onhand`
- Null rate trong sample: 0%
- Distinct ≈12; top: `0.00`×9, `144.00`×1, `226.00`×1, `8280.00`×1, `167.00`×1, `576460.00`×1, `800000.16`×1, `843776.10`×1

## Ghi chú thêm

- Giá trị tồn
