---
semantic_key: webrpt_inventory_daily__stock_status
title: webrpt inventory daily · stock status
display_names:
- stock_status
kind: text
tables:
- ref: db2:webrpt_inventory_daily
  column: stock_status
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Trạng thái tồn (WARN - Discontinued, INFO - Never Sold, …)
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for stock_status
- 'db2:webrpt_inventory_daily.stock_status: top=WARN - Discontinued(776), INFO - Never
  Sold(152), WARN - Slow Moving(71), CRIT - Dead Stock(1)'
---

# webrpt inventory daily · stock status

**Semantic key:** `webrpt_inventory_daily__stock_status` · **Cột vật lý:** `stock_status`

## Ý nghĩa nghiệp vụ

Cột STOCK_STATUS trên WEBRPT_INVENTORY_DAILY. db2:webrpt_inventory_daily: top INFO - Never Sold, WARN - Discontinued.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_inventory_daily` | `stock_status` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_inventory_daily.stock_status`
- Null rate trong sample: 0%
- Distinct ≈2; top: `INFO - Never Sold`×11, `WARN - Discontinued`×9

## Ghi chú thêm

- Trạng thái tồn (WARN - Discontinued, INFO - Never Sold, …)
