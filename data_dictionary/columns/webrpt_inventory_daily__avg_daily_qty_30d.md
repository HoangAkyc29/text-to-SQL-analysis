---
semantic_key: webrpt_inventory_daily__avg_daily_qty_30d
title: webrpt inventory daily · avg daily qty 30d
display_names:
- avg_daily_qty_30d
kind: measure
tables:
- ref: db2:webrpt_inventory_daily
  column: avg_daily_qty_30d
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Cột avg_daily_qty_30d
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for avg_daily_qty_30d
- 'db2:webrpt_inventory_daily.avg_daily_qty_30d: top=0.0000(997), 0.0667(1), 0.0338(1),
  0.0333(1)'
---

# webrpt inventory daily · avg daily qty 30d

**Semantic key:** `webrpt_inventory_daily__avg_daily_qty_30d` · **Cột vật lý:** `avg_daily_qty_30d`

## Ý nghĩa nghiệp vụ

Cột AVG_DAILY_QTY_30D trên WEBRPT_INVENTORY_DAILY. db2:webrpt_inventory_daily: top 0.0000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_inventory_daily` | `avg_daily_qty_30d` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_inventory_daily.avg_daily_qty_30d`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.0000`×20

## Ghi chú thêm

- Cột avg_daily_qty_30d
