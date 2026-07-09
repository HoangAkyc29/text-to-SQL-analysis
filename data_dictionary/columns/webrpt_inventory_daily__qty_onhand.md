---
semantic_key: webrpt_inventory_daily__qty_onhand
title: webrpt inventory daily · qty onhand
display_names:
- qty_onhand
kind: measure
tables:
- ref: db2:webrpt_inventory_daily
  column: qty_onhand
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Tồn kho hiện tại
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for qty_onhand
- 'db2:webrpt_inventory_daily.qty_onhand: top=0.0000(468), 1.0000(105), 2.0000(43),
  3.0000(27), 4.0000(24)'
---

# webrpt inventory daily · qty onhand

**Semantic key:** `webrpt_inventory_daily__qty_onhand` · **Cột vật lý:** `qty_onhand`

## Ý nghĩa nghiệp vụ

Cột QTY_ONHAND trên WEBRPT_INVENTORY_DAILY. db2:webrpt_inventory_daily: top 93.0000, 99.0000, 199.0000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_inventory_daily` | `qty_onhand` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_inventory_daily.qty_onhand`
- Null rate trong sample: 0%
- Distinct ≈20; top: `93.0000`×1, `99.0000`×1, `199.0000`×1, `144.0000`×1, `226.0000`×1, `0.2760`×1, `167.0000`×1, `74.0000`×1

## Ghi chú thêm

- Tồn kho hiện tại
